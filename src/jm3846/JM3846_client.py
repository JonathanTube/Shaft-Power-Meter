from abc import abstractmethod
import asyncio
import logging
from typing import Optional
from common.const_alarm_type import AlarmType
from jm3846.JM3846_0x03 import JM38460x03Async
from jm3846.JM3846_0x44 import JM38460x44Async
from jm3846.JM3846_0x45 import JM38460x45Async
from jm3846.JM3846_calculator import JM3846Calculator
from utils.alarm_saver import AlarmSaver
from utils.data_saver import DataSaver
from common.global_data import gdata
from websocket.websocket_server import ws_server


class JM3846AsyncClient:
    """基于asyncio的Modbus TCP异步客户端"""

    def __init__(self, name: str):
        self.name = name
        self.frame_size = 120
        self.total_frames = 0xFFFF

        self.timeout = 5
        self.running = False

        self.transaction_id = 0
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

        self.ch_sel_1 = None
        self.gain_1 = None
        self.ch_sel_0 = None
        self.gain_0 = None
        self.speed_sel = None
        self.sample_rate = None

        self.jm3846Calculator = JM3846Calculator()
        self._lock = asyncio.Lock()

    @abstractmethod
    def get_ip_port() -> tuple[str, int]:
        pass

    async def start(self, only_once=False) -> bool:
        """启动客户端"""
        try:
            self.running = True
            connected = await self.async_connect()
            if connected:
                await self.async_handle_0x44()
                # 异步接受数据
                asyncio.create_task(self.async_receive_looping())
            # return directly if only once.
            if only_once:
                return connected
            # if not, we need to retry.
            if not connected:
                await asyncio.sleep(2)
                await self.start()
        except Exception:
            logging.exception(f'{self.name} start JM3846 client failed')
            if only_once:
                return False
            await asyncio.sleep(5)
            await self.start()
        return False

    async def async_connect(self) -> bool:
        async with self._lock:  # 确保单线程重连
            """建立异步连接"""
            try:
                host, port = self.get_ip_port()
                logging.info(f'{self.name} JM3846 Connecting, host={host}, port={port}...')
                self.reader, self.writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=self.timeout
                )
                logging.info(f'{self.name} JM3846 Connected successfully')
                if self.name == 'sps1':
                    AlarmSaver.recovery(alarm_type=AlarmType.SPS1_DISCONNECTED)
                elif self.name == 'sps2':
                    AlarmSaver.recovery(alarm_type=AlarmType.SPS2_DISCONNECTED)
                return True
            except Exception:
                logging.exception(f'{self.name} JM3846 Connection error')
                self.set_offline(True)
                if self.name == 'sps1':
                    AlarmSaver.create(alarm_type=AlarmType.SPS1_DISCONNECTED)
                elif self.name == 'sps2':
                    AlarmSaver.create(alarm_type=AlarmType.SPS2_DISCONNECTED)

            return False

    async def async_disconnect(self) -> bool:
        """断开连接"""
        try:
            self.running = False
            if self.writer:
                # 发送0x45,断开数据流
                await self.async_handle_0x45()
                self.writer.close()
                await self.writer.wait_closed()
                logging.info(f'{self.name} JM3846 Connection closed')
                self.set_offline(True)
                return True
        except Exception:
            logging.exception(f'{self.name} disconnect from sps failed')
        return False

    async def async_handle_0x03(self):
        """异步处理功能码0x03"""
        try:
            self.transaction_id = (self.transaction_id + 1) % 0xFFFF
            # 发送请求
            request = JM38460x03Async.build_request(self.transaction_id)
            self.writer.write(request)
            await self.writer.drain()
        except asyncio.TimeoutError:
            logging.exception(f'{self.name} JM3846 0x03 request timeout')
        except Exception:
            logging.exception(f'{self.name} JM3846 0x03 error')

    def _update_config(self, config: dict):
        """更新设备配置"""
        self.ch_sel_1 = config['ch_sel_1']
        self.gain_1 = config['gain_1']
        self.ch_sel_0 = config['ch_sel_0']
        self.gain_0 = config['gain_0']
        self.speed_sel = config['speed_sel']
        self.sample_rate = config['sample_rate']

    async def async_handle_0x44(self):
        """异步处理功能码0x44"""
        try:
            self.transaction_id = (self.transaction_id + 1) % 0xFFFF

            request = JM38460x44Async.build_request(
                tid=self.transaction_id,
                frame_size=self.frame_size,
                total_frames=self.total_frames
            )
            logging.info(f'{self.name} send 0x44 req={request}')
            self.writer.write(request)
            await self.writer.drain()

        except asyncio.TimeoutError:
            logging.exception(f'{self.name} JM3846 0x44 request timeout')
        except Exception:
            logging.exception(f'{self.name} JM3846 0x44 error')

    async def async_receive_looping(self):
        """持续接收0x44数据"""
        while self.running:
            try:
                await asyncio.sleep(5)
                if self.name == 'sps2' and int(gdata.amount_of_propeller) == 1:
                    logging.info('exit running since single propeller')
                    gdata.sps2_offline = True
                    return

                # 接收响应
                response = await asyncio.wait_for(
                    self.reader.read(256),
                    timeout=self.timeout * 2
                )

                if not response:
                    await asyncio.sleep(2)
                    continue

                # 基本头长度检查
                if len(response) < 8:
                    logging.exception(f'{self.name} the length of return is invalid.')
                    continue

                # 解析功能码
                func_code = response[7]

                # 异常响应处理
                if func_code & 0x80:
                    error_code = response[8] if len(response) >= 9 else 0
                    logging.exception(f'{self.name} SPS return errors, error_code is {error_code}')
                    continue

                if func_code == 0x03:
                    res = JM38460x03Async.parse_response(response)
                    if res['success']:
                        config = res['values']
                        self._update_config(config)
                    continue

                if func_code == 0x44:
                    # 检查配置信息
                    if any(v is None for v in [self.ch_sel_1, self.ch_sel_0, self.speed_sel]):
                        await self.async_handle_0x03()
                        continue

                    res = JM38460x44Async.parse_response(
                        response,
                        frame_size=self.frame_size,
                        sample_rate=self.sample_rate,
                        ch_sel1=self.ch_sel_1,
                        ch_sel0=self.ch_sel_0,
                        speed_sel=self.speed_sel
                    )

                    if res['success']:
                        self.set_offline(False)
                        first_frame_per_second = res['first_frame_per_second']
                        if first_frame_per_second:
                            # 只处理1s内数据的第一帧
                            await self.save_0x44_result(res['values'])

                        current_frame = res['current_frame']
                        if current_frame >= self.total_frames:
                            await self.async_handle_0x45()
                            await self.async_handle_0x44()
                    continue

                if func_code == 0x45:
                    res = JM38460x45Async.parse_response(response)
                    logging.info(f'{self.name} JM3846 0x45 Response: {res}')
                    continue

            except asyncio.TimeoutError:
                logging.exception(f'{self.name} JM3846 0x44 receive timeout, retrying...')
                self.set_offline(True)
                if self.name == 'sps1':
                    AlarmSaver.create(alarm_type=AlarmType.SPS1_DISCONNECTED)
                elif self.name == 'sps2':
                    AlarmSaver.create(alarm_type=AlarmType.SPS2_DISCONNECTED)
            except ConnectionResetError as e:
                logging.exception(f'{self.name} JM3846 Connection reset: {e}')
                self.set_offline(True)
                self.running = False
                await self.async_connect()
            except Exception:
                logging.exception(f'{self.name} JM3846 0x44 Receive error')

    async def save_0x44_result(self, result: dict):
        try:
            # logging.info('result=', result)
            if gdata.test_mode_running:
                logging.info('test mode is running, skip save 0x44 result from JM3456.')
                return
            """数据存储方法"""
            torque = 0
            thrust = 0
            speed = 0

            json_data = {
                'type': 'sps_data',
                'name': self.name
            }
            if 'ch0_ad' in result:
                ad0 = round(result['ch0_ad'], 2)
                ad0_mv_per_v = self.jm3846Calculator.calculate_mv_per_v(ad0, self.gain_0)

                if self.name == 'sps1':
                    gdata.sps1_ad0 = ad0
                    gdata.sps1_mv_per_v_for_torque = ad0_mv_per_v
                else:
                    gdata.sps2_ad0 = ad0
                    gdata.sps2_mv_per_v_for_torque = ad0_mv_per_v

                # 加上偏移量
                torque_offset = gdata.sps1_torque_offset if self.name == 'sps1' else gdata.sps2_torque_offset
                ad0_microstrain = self.jm3846Calculator.calculate_microstrain(ad0_mv_per_v + torque_offset)
                torque = self.jm3846Calculator.calculate_torque(ad0_microstrain)
                logging.info(f'name={self.name},ad0={ad0}, ad0_mv_per_v={ad0_mv_per_v}, torque_offset={torque_offset}, microstrain={ad0_microstrain}, torque={torque}')
                json_data['torque'] = torque
            if 'ch1_ad' in result:
                ad1 = round(result['ch1_ad'], 2)
                ad1_mv_per_v = self.jm3846Calculator.calculate_mv_per_v(ad1, self.gain_1)

                if self.name == 'sps1':
                    gdata.sps1_ad1 = ad1
                    gdata.sps1_mv_per_v_for_thrust = ad1_mv_per_v
                else:
                    gdata.sps2_ad1 = ad1
                    gdata.sps2_mv_per_v_for_thrust = ad1_mv_per_v

                # 加上偏移量
                thrust_offset = gdata.sps1_thrust_offset if self.name == 'sps1' else gdata.sps2_thrust_offset
                thrust = self.jm3846Calculator.calculate_thrust(ad1_mv_per_v + thrust_offset)
                logging.info(f'name={self.name},ad1={ad1},ad1_mv_per_v={ad1_mv_per_v}, thrust_offset={thrust_offset}, thrust={thrust}')
                json_data['thrust'] = thrust
            if 'rpm' in result:
                rpm = round(result['rpm'], 2)
                if self.name == 'sps1':
                    gdata.sps1_speed = rpm
                else:
                    gdata.sps2_speed = rpm

                speed = round(rpm / 10, 1)
                logging.info(f'name={self.name},rpm={rpm}, speed={speed}')
                json_data['rpm'] = rpm
            DataSaver.save(self.name, torque, thrust, speed)

            # 如果作为服务端，那需要向外发送数据
            if gdata.hmi_server_started:
                await ws_server.broadcast(json_data)
        except Exception as e:
            logging.exception(e)

    async def async_handle_0x45(self):
        """异步处理功能码0x45"""
        try:
            self.transaction_id = (self.transaction_id + 1) % 0xFFFF

            request = JM38460x45Async.build_request(self.transaction_id)
            if not self.writer:
                return

            logging.info(f'{self.name} send 0x45 req={request}')
            self.writer.write(request)
            await self.writer.drain()
        except asyncio.TimeoutError:
            logging.exception(f'{self.name} JM3846 0x45 request timeout')
        except Exception:
            logging.exception(f'{self.name} JM3846 0x45 error')

    def set_offline(self, is_offline: bool):
        if self.name == 'sps1':
            gdata.sps1_offline = is_offline
        elif self.name == 'sps2':
            gdata.sps2_offline = is_offline
