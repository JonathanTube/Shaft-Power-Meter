import asyncio
import logging
import struct
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional, List
from jm3846.JM3846_0x03 import JM38460x03Async
from jm3846.JM3846_0x44 import JM38460x44Async
from jm3846.JM3846_0x45 import JM38460x45Async


class ClientState(Enum):
    STOPPED = auto()   # 未运行
    RUNNING = auto()   # 正常工作
    CANCELED = auto()  # 被主动关闭


class JM3846AsyncClient(ABC):
    """基于asyncio的Modbus TCP异步客户端（通用父类）"""

    def __init__(self, name: str):
        self.name = name
        self.frame_size = 120
        self.total_frames = 0xFFFF
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()
        self._retry_times = 0
        self._max_retries = 6
        self.state = ClientState.STOPPED
        self._bg_tasks: List[asyncio.Task] = []
        self._receive_0x44_task: Optional[asyncio.Task] = None

    async def connect(self):
        """建立连接并启动后台接收任务"""
        async with self._lock:
            self.state = ClientState.STOPPED
            self._retry_times = 0

            while self._retry_times < self._max_retries:
                if self.state == ClientState.CANCELED:
                    break

                try:
                    host, port = self.get_ip_port()
                    logging.info(f'[JM3846-{self.name}] Connecting to {host}:{port}')
                    self.reader, self.writer = await asyncio.wait_for(
                        asyncio.open_connection(host, port), timeout=10
                    )

                    # 启动子类定义的后台任务
                    self.start_background_tasks()

                    # 先发0x45，再发0x03，再发0x44
                    await self.handle_0x45()
                    if not await self.handle_0x03():
                        continue

                    await self.async_handle_0x44()

                except asyncio.TimeoutError:
                    logging.error(f'[JM3846-{self.name}] connection timeout')
                    self.set_offline(True)
                except Exception:
                    logging.exception(f'[JM3846-{self.name}] connection failed')
                    self.set_offline(True)
                finally:
                    if self.state != ClientState.CANCELED:
                        await asyncio.sleep(2 ** self._retry_times)
                        self._retry_times += 1

            self.set_offline(True)

    async def handle_0x03(self) -> bool:
        """功能码0x03：读取配置参数"""
        request = JM38460x03Async.build_request()
        logging.info(f'[JM3846-{self.name}] send 0x03 req hex={bytes.hex(request)}')
        self.writer.write(request)
        await self.writer.drain()

        response = await self._read_frame(timeout=30)
        func_code = struct.unpack(">B", response[7:8])[0]
        if func_code == 0x03:
            JM38460x03Async.parse_response(response, self.name)
            return True
        return False

    async def async_handle_0x44(self):
        """功能码0x44：请求多帧数据"""
        request = JM38460x44Async.build_request(self.frame_size, self.total_frames)
        logging.info(f'[JM3846-{self.name}] send 0x44 req hex={bytes.hex(request)}')
        self.writer.write(request)
        await self.writer.drain()

        self.state = ClientState.RUNNING
        self._receive_0x44_task = asyncio.create_task(self.receive_0x44())
        await self._receive_0x44_task

    async def receive_0x44(self):
        """持续接收数据"""
        while self.state == ClientState.RUNNING:
            try:
                response = await self._read_frame(timeout=30)
                func_code = struct.unpack(">B", response[7:8])[0]

                # 异常码
                if func_code & 0x80:
                    continue

                if func_code == 0x44:
                    current_frame = JM38460x44Async.parse_response(response, self.name)
                    self.set_offline(False)

                    if current_frame >= self.total_frames:
                        await self.handle_0x45()
                        await self.async_handle_0x44()

            except asyncio.CancelledError:
                raise
            except Exception:
                self.set_offline(True)
                return

    async def handle_0x45(self) -> bool:
        """功能码0x45：断开数据流"""
        request = JM38460x45Async.build_request()
        logging.info(f'[JM3846-{self.name}] send 0x45 req hex={bytes.hex(request)}')
        self.writer.write(request)
        await self.writer.drain()

        response = await self._read_frame(timeout=10)
        func_code = struct.unpack(">B", response[7:8])[0]
        if func_code == 0x45:
            res_0x45 = JM38460x45Async.parse_response(response)
            if res_0x45 == 0x45:
                logging.info(f'[JM3846-{self.name}] stop 0x44 successfully')
            return True
        return False

    async def _read_frame(self, timeout: float = 30.0) -> bytes:
        """按 Modbus TCP(MBAP) 帧格式读取一帧"""
        try:
            header = await asyncio.wait_for(self.reader.readexactly(6), timeout=timeout)
            length = struct.unpack('>H', header[4:6])[0]
            if length < 2 or length > 2048:
                raise ValueError(f"Invalid MBAP length: {length}")
            body = await asyncio.wait_for(self.reader.readexactly(length), timeout=timeout)
            return header + body
        except asyncio.IncompleteReadError:
            logging.error(f"[JM3846-{self.name}] connection closed by remote")
            self.set_offline(True)
            raise  # 让上层任务退出

    def set_offline(self, is_offline: bool):
        """切换离线/在线状态"""
        if is_offline:
            self.state = ClientState.STOPPED
            self.create_alarm_hook()
        else:
            self._retry_times = 0
            self.recovery_alarm_hook()

        self.set_offline_hook(is_offline)

    async def close(self):
        """终止一切运行，关闭资源"""
        self.state = ClientState.CANCELED

        if self._receive_0x44_task:
            self._receive_0x44_task.cancel()
            await asyncio.gather(self._receive_0x44_task, return_exceptions=True)

        # 调用子类停止后台任务
        self.stop_background_tasks()

        if self.writer:
            try:
                await asyncio.wait_for(self.handle_0x45(), timeout=3)
            except asyncio.TimeoutError:
                pass
            self.writer.close()
            await self.writer.wait_closed()

        self.writer = None
        self.reader = None
        self.set_offline_hook(True)

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

    @abstractmethod
    def start_background_tasks(self):
        """启动后台任务（子类实现）"""
        pass

    @abstractmethod
    def stop_background_tasks(self):
        """停止后台任务（子类实现）"""
        pass
