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
        self._bg_tasks: List[asyncio.Task] = []
        self.is_canceled = False

    async def connect(self):
        """建立连接并启动后台接收任务（固定间隔无限重连）"""
        self.is_canceled = False
        while not self.is_canceled:
            try:
                async with self._lock:
                    host, port = self.get_ip_port()
                    logging.info(f'[JM3846-{self.name}] 正在连接 {host}:{port}')
                    self.reader, self.writer = await asyncio.wait_for(
                        asyncio.open_connection(host, port),
                        timeout=10
                    )
                    logging.info(f'[JM3846-{self.name}] 连接成功 {host}:{port}')
                    self.start_background_tasks()
                    await JM38460x45.handle(self.name, self.reader, self.writer)
                    await JM38460x03.handle(self.name, self.reader, self.writer)

                # 0x44 循环放到锁外执行
                await JM38460x44.handle(self.name, self.reader, self.writer, self.set_online, self.set_offline)

            except ConnectionRefusedError as e:
                logging.error(f'[JM3846-{self.name}] 连接被拒绝: {e}')
            except asyncio.TimeoutError:
                logging.info(f'[JM3846-{self.name}] 连接超时')
                pass
            except asyncio.CancelledError:
                logging.info(f'[JM3846-{self.name}] 连接任务被取消')
                break
            except Exception as e:
                logging.exception(f'[JM3846-{self.name}] 连接异常: {e}')

            await self.release()
            await asyncio.sleep(5)  # 固定 5 秒重试

    async def close(self):
        """强制退出连接"""
        self.is_canceled = True
        await self.release()

    async def release(self):
        """终止所有运行任务并关闭资源"""
        try:
            JM38460x44.stop()
            self.stop_background_tasks()

            if self.writer:
                try:
                    if not self.writer.is_closing():
                        try:
                            await JM38460x45.handle(self.name, self.reader, self.writer)
                        except Exception:
                            logging.warning(f'[JM3846-{self.name}] 发送 0x45 停止帧时失败（已忽略）')

                        self.writer.close()
                        # 改为（安全）
                        try:
                            loop = asyncio.get_running_loop()
                            loop.create_task(self.writer.wait_closed())
                        except RuntimeError:
                            # 没有运行 loop，忽略等待
                            pass
                except Exception:
                    logging.warning(f'[JM3846-{self.name}] 关闭连接时出错（已忽略）')

        except Exception:
            logging.exception(f'[JM3846-{self.name}] release 释放资源时发生异常')
        finally:
            self.writer = None
            self.reader = None
            self.set_offline()

    # ---- 抽象方法 ----

    @abstractmethod
    def get_ip_port(self) -> tuple[str, int]:
        pass

    @abstractmethod
    def set_online(self):
        pass

    @abstractmethod
    def set_offline(self):
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
