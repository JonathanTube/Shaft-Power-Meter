import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional, List
from jm3846.JM3846_0x03 import JM38460x03
from jm3846.JM3846_0x44 import JM38460x44
from jm3846.JM3846_0x45 import JM38460x45
from jm3846.JM3846_torque_rpm import jm3846_torque_rpm
from jm3846.JM3846_thrust import jm3846_thrust


class JM3846AsyncClient(ABC):
    """基于asyncio的Modbus TCP异步客户端（通用父类）"""

    def __init__(self, name: str):
        self.name = name
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()
        self._retry_times = 0
        self._max_retries = 6
        self._bg_tasks: List[asyncio.Task] = []

    async def connect(self):
        """建立连接并启动后台接收任务"""
        self._retry_times = 0
        while self._retry_times < self._max_retries:
            try:
                logging.info(f'[JM3846-{self.name}] 尝试第{self._retry_times + 1}次连接')
                # 连接建立和初始化放在锁里，长循环移到锁外，避免锁死
                async with self._lock:
                    host, port = self.get_ip_port()
                    logging.info(f'[JM3846-{self.name}] 正在连接 {host}:{port}')
                    self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=10)
                    logging.info(f'[JM3846-{self.name}] 连接成功 {host}:{port}')
                    self.start_background_tasks()
                    await JM38460x45.handle(self.name, self.reader, self.writer)
                    await JM38460x03.handle(self.name, self.reader, self.writer)
                    self.recovery_alarm_hook()
                    self.set_offline_hook(False)

                # 0x44 循环放到锁外执行
                await JM38460x44.handle(self.name, self.reader, self.writer)
            except ConnectionRefusedError as e:
                logging.exception(f'[JM3846-{self.name}] connect refused error {e}')
            except Exception as e:
                logging.exception(f'[JM3846-{self.name}] connect error {e}')

            await self.release()
            await asyncio.sleep(2 ** self._retry_times)
            self._retry_times += 1

    async def close(self):
        self._retry_times = self._max_retries + 1  # 强制 connect 循环退出
        await self.release()

    async def release(self):
        """终止所有运行任务并关闭资源"""
        try:
            # 停止 0x44 数据读取
            JM38460x44.stop()

            # 停止后台任务
            self.stop_background_tasks()

            # 关闭连接
            if self.writer:
                try:
                    if not self.writer.is_closing():
                        try:
                            await JM38460x45.handle(self.name, self.reader, self.writer)  # 发送 0x45 停止帧
                        except Exception:
                            logging.warning(f'[JM3846-{self.name}] 发送 0x45 停止帧时失败（已忽略）')

                        self.writer.close()
                        try:
                            await self.writer.wait_closed()
                        except Exception:
                            logging.warning(f'[JM3846-{self.name}] 等待连接关闭时发生异常（已忽略）')
                except Exception:
                    logging.warning(f'[JM3846-{self.name}] 关闭连接时出错（已忽略）')

        except Exception:
            logging.exception(f'[JM3846-{self.name}] release 释放资源时发生异常')
        finally:
            # 触发离线告警
            self.create_alarm_hook()
            self.set_offline_hook(True)
            self.writer = None
            self.reader = None

    # ---- 抽象方法 ----

    @abstractmethod
    def get_ip_port(self) -> tuple[str, int]:
        pass

    @abstractmethod
    def set_offline_hook(self, is_offline: bool):
        pass

    @abstractmethod
    def create_alarm_hook(self):
        pass

    @abstractmethod
    def recovery_alarm_hook(self):
        pass

    def start_background_tasks(self):
        if not jm3846_torque_rpm.is_running():
            self._bg_tasks.append(asyncio.create_task(jm3846_torque_rpm.start(self.name)))
        if not jm3846_thrust.is_running():
            self._bg_tasks.append(asyncio.create_task(jm3846_thrust.start(self.name)))

    def stop_background_tasks(self):
        jm3846_torque_rpm.stop()
        jm3846_thrust.stop()
        for t in self._bg_tasks:
            if not t.done():
                t.cancel()
        self._bg_tasks.clear()
