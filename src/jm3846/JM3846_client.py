import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional, List
from jm3846.JM3846_0x03 import JM38460x03
from jm3846.JM3846_0x44 import JM38460x44
from jm3846.JM3846_0x45 import JM38460x45
from jm3846.JM3846_torque_rpm import jm3846_torque_rpm
from jm3846.JM3846_thrust import jm3846_thrust


class ClientState(Enum):
    STOPPED = auto()   # 未运行
    RUNNING = auto()   # 正常工作
    CANCELED = auto()  # 被主动关闭


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
        self._receive_0x44_task: Optional[asyncio.Task] = None

    async def connect(self):
        """建立连接并启动后台接收任务"""
        async with self._lock:
            self._retry_times = 0

            while self._retry_times < self._max_retries:
                try:
                    host, port = self.get_ip_port()
                    logging.info(f'[JM3846-{self.name}] Connecting to {host}:{port}')
                    self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=10)
                    # 启动子类定义的后台任务
                    self.start_background_tasks()
                    # 先发0x45，再发0x03，再发0x44
                    await JM38460x45.handle(self.name, self.reader, self.writer)
                    await JM38460x03.handle(self.name, self.reader, self.writer)
                    self.recovery_alarm_hook()
                    self.set_offline_hook(False)
                    await JM38460x44.handle(self.name, self.reader, self.writer)
                except:
                    logging.exception(f'[JM3846-{self.name}] exception occured')
                    await self.close()
                finally:
                    await asyncio.sleep(2 ** self._retry_times)
                    self._retry_times += 1

    async def close(self):
        """终止一切运行，关闭资源"""
        # 关闭循环
        JM38460x44.running = False
        self.create_alarm_hook()
        # 调用子类停止后台任务
        self.stop_background_tasks()
        # 这只离线状态
        self.set_offline_hook(True)

        if self._receive_0x44_task:
            self._receive_0x44_task.cancel()
            await asyncio.gather(self._receive_0x44_task, return_exceptions=True)

        if self.writer:
            try:
                await asyncio.wait_for(self.handle_0x45(), timeout=3)
            except asyncio.TimeoutError:
                pass
            self.writer.close()
            await self.writer.wait_closed()

        self.writer = None
        self.reader = None

    # ---- 抽象方法 ----

    @abstractmethod
    def get_ip_port(self) -> tuple[str, int]:
        """返回 (host, port)"""
        pass

    @abstractmethod
    def set_offline_hook(self, is_offline: bool):
        """设置离线/在线状态"""
        pass

    @abstractmethod
    def create_alarm_hook(self):
        """创建离线告警"""
        pass

    @abstractmethod
    def recovery_alarm_hook(self):
        """恢复在线告警"""
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
