from abc import abstractmethod
import asyncio
import logging
import struct
from typing import Optional
from common.const_alarm_type import AlarmType
from jm3846.JM3846_0x03 import JM38460x03Async
from jm3846.JM3846_0x44 import JM38460x44Async
from jm3846.JM3846_0x45 import JM38460x45Async
from jm3846.JM3846_torque_rpm import jm3846_torque_rpm
from jm3846.JM3846_thrust import jm3846_thrust
from utils.alarm_saver import AlarmSaver
from common.global_data import gdata


class JM3846AsyncClient:
    """基于asyncio的Modbus TCP异步客户端"""

    def __init__(self, name: str):
        self.name = name
        self.frame_size = 120
        self.total_frames = 0xFFFF

        self.transaction_id = 0
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

        self._lock = asyncio.Lock()

        self._retry = 0
        self._max_retries = 6

        self._is_running = False
        self._is_canceled = False

        self.timeoutTimes = 10

    @property
    def is_connected(self):
        if self.name == 'sps':
            return not gdata.configSPS.is_offline
        return not gdata.configSPS2.is_offline

    @abstractmethod
    def get_ip_port() -> tuple[str, int]:
        pass

    async def connect(self):
        async with self._lock:  # 确保单线程重连
            self._is_canceled = False
            self._retry = 0  # 重置重试计数器

            while gdata.configCommon.is_master and self._retry < self._max_retries:
                self.timeoutTimes = 10  # 重置超时最大次数
                if self._is_canceled:
                    break

                try:
                    host, port = self.get_ip_port()

                    logging.info(f'[***{self.name}***] JM3846 Connecting, host={host}, port={port}...')

                    self.reader, self.writer = await asyncio.wait_for(
                        asyncio.open_connection(host, port),
                        timeout=10
                    )

                    if not jm3846_torque_rpm.is_running():
                        # 启动处理Torque和rpm的任务,2s一次
                        asyncio.create_task(jm3846_torque_rpm.start(self.name))

                    if not jm3846_thrust.is_running():
                        # 启动处理thrust的任务，10s一次
                        asyncio.create_task(jm3846_thrust.start(self.name))

                    logging.info(f'[***{self.name}***] JM3846 Connected successfully')
                    # 发送0x45,断开数据流,send 0x45 to sps while reconnecting.
                    await self.async_handle_0x45()
                    # 请求配置参数
                    await self.async_handle_0x03()
                    # 请求多帧数据
                    await self.async_handle_0x44()
                    # 设置运作中
                    self._is_running = True
                    # 启动接收任务, 这里是阻塞的，不然外部一直循环
                    await self.async_receive_looping()
                except TimeoutError:
                    logging.error(f'[***{self.name}***] start JM3846 client timeout')
                    self.set_offline(True)
                except:
                    logging.error(f'[***{self.name}***] start JM3846 client failed')
                    self.set_offline(True)
                finally:
                    if not self._is_canceled:  # 只有未取消时才执行退避
                        seconds = 2 ** self._retry
                        logging.info(f'[***{self.name}***] JM3846 retry times = {self._retry}, wait for {seconds}s to reconnect')
                        await asyncio.sleep(seconds)
                        self._retry += 1

            self.set_offline(True)
            self._is_canceled = False

    async def close(self):
        self._is_canceled = True

        if self.name == 'sps':
            gdata.configSPS.is_offline = True
        elif self.name == 'sps2':
            gdata.configSPS2.is_offline = True

        try:
            self._is_running = False
            jm3846_torque_rpm.stop()
            jm3846_thrust.stop()
            if self.writer:
                # 发送0x45,断开数据流
                await self.async_handle_0x45()
                self.writer.close()
                await self.writer.wait_closed()
                logging.info(f'[***{self.name}***] JM3846 Connection closed')
        except:
            logging.exception(f'[***{self.name}***] JM3846 disconnect from sps failed')
        finally:
            self.writer = None
            self.reader = None
            self._is_running = False

    async def async_handle_0x03(self):
        """异步处理功能码0x03"""
        self.transaction_id = (self.transaction_id + 1) % 0xFFFF
        # 发送请求
        request = JM38460x03Async.build_request(self.transaction_id)

        if not self.writer:
            return

        logging.info(f'[***{self.name}***] JM3846 0x03 req = {bytes.hex(request)}')
        self.writer.write(request)
        await self.writer.drain()

    async def async_handle_0x44(self):
        """异步处理功能码0x44"""
        self.transaction_id = (self.transaction_id + 1) % 0xFFFF

        request = JM38460x44Async.build_request(
            tid=self.transaction_id,
            frame_size=self.frame_size,
            total_frames=self.total_frames
        )

        if not self.writer:
            return

        logging.info(f'[***{self.name}***] JM3846 send 0x44 req={bytes.hex(request)}')
        self.writer.write(request)
        await self.writer.drain()

    async def async_receive_looping(self):
        """持续接收数据"""
        while self._is_running:
            try:
                if self.name == 'sps2' and int(gdata.configCommon.amount_of_propeller) == 1:
                    logging.info('exit running since single propeller')
                    gdata.configSPS2.is_offline = True
                    return

                # 接收响应
                response = await asyncio.wait_for(self.reader.read(256), timeout=30)

                logging.info(f'raw_data from sps={bytes.hex(response)}')

                if response == b'':
                    break

                # 基本头长度检查
                if len(response) < 8:
                    logging.error(f'[***{self.name}***] the length of return is invalid.')
                    continue

                # 解析功能码
                func_code = struct.unpack(">B", response[7:8])[0]

                logging.info(f'[***{self.name}***] func_code={func_code}')

                # 异常响应处理
                if func_code & 0x80:
                    error_code = response[8] if len(response) >= 9 else 0
                    logging.error(f'[***{self.name}***] SPS return errors, error_code is {error_code}')
                    continue

                if func_code == 0x03:
                    JM38460x03Async.parse_response(response, self.name)
                    continue

                if func_code == 0x44:
                    ch_sel_1 = gdata.configSPS.ch_sel_1 if self.name == 'sps' else gdata.configSPS2.ch_sel_1
                    ch_sel_0 = gdata.configSPS.ch_sel_0 if self.name == 'sps' else gdata.configSPS2.ch_sel_0
                    speed_sel = gdata.configSPS.speed_sel if self.name == 'sps' else gdata.configSPS2.speed_sel
                    # 检查配置信息
                    if any(v is None for v in [ch_sel_1, ch_sel_0, speed_sel]):
                        # 配置参数为空，直接跳过
                        logging.info("sps config. hasn't been gotten.")
                        continue

                    current_frame: int = JM38460x44Async.parse_response(response, self.name)

                    self.set_offline(False)

                    if current_frame >= self.total_frames:
                        await self.async_handle_0x45()
                        await self.async_handle_0x44()

                    continue

                if func_code == 0x45:
                    JM38460x45Async.parse_response(response)
                    continue

            except TimeoutError:
                logging.error(f'[***{self.name}***] JM3846 receive data timeout, retry times left = {self.timeoutTimes}')
                self.timeoutTimes -= 1
                if self.timeoutTimes <= 0:
                    logging.error(f'[***{self.name}***] JM3846 timeout too many times, reconnect...')
                    self.set_offline(True)
                    return
            except ConnectionResetError as e:
                logging.error(f'[***{self.name}***] JM3846 Connection reset: {e}')
                self.set_offline(True)
                return
            except:
                logging.exception(f'[***{self.name}***] JM3846 0x44 Receive error')
                self.set_offline(True)
                return

    async def async_handle_0x45(self):
        """异步处理功能码0x45"""
        try:
            self.transaction_id = (self.transaction_id + 1) % 0xFFFF

            request = JM38460x45Async.build_request(self.transaction_id)
            if not self.writer:
                return

            logging.info(f'[***{self.name}***] send 0x45 req={bytes.hex(request)}')
            self.writer.write(request)
            await self.writer.drain()
        except asyncio.TimeoutError:
            logging.error(f'[***{self.name}***] JM3846 0x45 request timeout')
        except Exception:
            logging.error(f'[***{self.name}***] JM3846 0x45 error')

    def set_offline(self, is_offline: bool):
        if is_offline:
            self._is_running = False
            jm3846_torque_rpm.stop()
            jm3846_thrust.stop()
            self.create_alarm()
        else:
            self._retry = 0
            self.recovery_alarm()

        if self.name == 'sps':
            gdata.configSPS.is_offline = is_offline
        elif self.name == 'sps2':
            gdata.configSPS2.is_offline = is_offline

    def create_alarm(self):
        if self.name == 'sps':
            AlarmSaver.create(alarm_type=AlarmType.MASTER_SPS_DISCONNECTED)
        elif self.name == 'sps2':
            AlarmSaver.create(alarm_type=AlarmType.MASTER_SPS2_DISCONNECTED)

    def recovery_alarm(self):
        if self.name == 'sps':
            AlarmSaver.recovery(
                alarm_type_occured=AlarmType.MASTER_SPS_DISCONNECTED,
                alarm_type_recovered=AlarmType.MASTER_SPS_CONNECTED
            )
        elif self.name == 'sps2':
            AlarmSaver.recovery(
                alarm_type_occured=AlarmType.MASTER_SPS2_DISCONNECTED,
                alarm_type_recovered=AlarmType.MASTER_SPS2_CONNECTED
            )
