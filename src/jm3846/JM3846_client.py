import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional, List
from jm3846.JM3846_0x03 import JM38460x03
from jm3846.JM3846_0x44 import JM38460x44
from jm3846.JM3846_0x45 import JM38460x45
from jm3846.JM3846_data_handler_for_ns import jm3846_data_handler_for_ns
from jm3846.JM3846_data_handler_for_1s import jm3846_data_handler_for_1s
from jm3846.JM3846_data_handler_for_15s import jm3846_data_handler_for_15s


class JM3846AsyncClient(ABC):
    """基于asyncio的Modbus TCP异步客户端（通用父类）"""

    def __init__(self, name: str):
        self.name = name
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()
        self._bg_tasks: List[asyncio.Task] = []
        self.is_canceled = False
        self._connect_task: Optional[asyncio.Task] = None

    async def start(self):
        """启动异步连接任务（不阻塞外部）"""
        if self._connect_task is None or self._connect_task.done():
            self.is_canceled = False
            self._connect_task = asyncio.create_task(self._connect_loop())

    async def _connect_loop(self):
        """后台循环连接任务"""
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
            except asyncio.CancelledError:
                logging.info(f'[JM3846-{self.name}] 连接任务被取消')
                break
            except Exception as e:
                logging.exception(f'[JM3846-{self.name}] 连接异常: {e}')

            await self.release()
            if not self.is_canceled:
                await asyncio.sleep(10)  # 固定10秒重试

    async def close(self):
        """强制退出连接"""
        self.is_canceled = True
        if self._connect_task and not self._connect_task.done():
            self._connect_task.cancel()
            try:
                await self._connect_task
            except asyncio.CancelledError:
                pass
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
                        try:
                            await self.writer.wait_closed()
                        except Exception:
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
        if not jm3846_data_handler_for_ns.is_running():
            self._bg_tasks.append(asyncio.create_task(jm3846_data_handler_for_ns.start(self.name)))

        if not jm3846_data_handler_for_1s.is_running():
            self._bg_tasks.append(asyncio.create_task(jm3846_data_handler_for_1s.start(self.name)))

        if not jm3846_data_handler_for_15s.is_running():
            self._bg_tasks.append(asyncio.create_task(jm3846_data_handler_for_15s.start(self.name)))

    def stop_background_tasks(self):
        jm3846_data_handler_for_ns.stop()
        jm3846_data_handler_for_1s.stop()
        jm3846_data_handler_for_15s.stop()
        for t in self._bg_tasks:
            if not t.done():
                t.cancel()
        self._bg_tasks.clear()
