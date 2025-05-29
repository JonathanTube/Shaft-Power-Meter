import asyncio
from typing import Optional
from jm3846.JM3846_0x03 import JM38460x03Async
from jm3846.JM3846_0x44 import JM38460x44Async
from jm3846.JM3846_0x45 import JM38460x45Async
from jm3846.JM3846_calculator import JM3846Calculator
from db.models.io_conf import IOConf
from utils.data_saver import DataSaver


class JM3846AsyncClient:
    """基于asyncio的Modbus TCP异步客户端"""

    def __init__(self):
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

        self.jm3846Calculator = JM3846Calculator()
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        """启动客户端"""
        await self.async_connect()
        asyncio.create_task(self.async_receive_looping_0x44())
        await self.async_handle_0x44()

    async def async_connect(self) -> None:
        """建立异步连接"""
        try:
            print('JM3846 Connecting...')
            io_conf: IOConf = IOConf.get()
            host = io_conf.sps1_ip
            port = io_conf.sps2_port
            self.reader, self.writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=self.timeout
            )
            self.running = True
            print('JM3846 Connected successfully')
        except Exception as e:
            print(f'JM3846 Connection error: {e}')
            raise

    async def async_disconnect(self) -> None:
        """断开连接"""
        self.running = False
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            print('JM3846 Connection closed')

    async def async_handle_0x03(self):
        """异步处理功能码0x03"""
        async with self._lock:
            try:
                self.transaction_id = (self.transaction_id + 1) % 0xFFFF

                # 发送请求
                request = JM38460x03Async.build_request(self.transaction_id)
                self.writer.write(request)
                await self.writer.drain()

                # 接收响应
                response = await asyncio.wait_for(
                    self.reader.read(256),
                    timeout=self.timeout
                )

                res = JM38460x03Async.parse_response(response)
                print(f'JM3846 0x03 Response: {res}')

                if res['success']:
                    config = res['values']
                    self._update_config(config)

            except asyncio.TimeoutError:
                print('JM3846 0x03 request timeout')
            except Exception as e:
                print(f'JM3846 0x03 error: {e}')
                await self.async_disconnect()

    def _update_config(self, config: dict):
        """更新设备配置"""
        self.ch_sel_1 = config['ch_sel_1']
        self.gain_1 = config['gain_1']
        self.ch_sel_0 = config['ch_sel_0']
        self.gain_0 = config['gain_0']
        self.speed_sel = config['speed_sel']

    async def async_handle_0x44(self):
        """异步处理功能码0x44"""
        async with self._lock:
            try:
                self.transaction_id = (self.transaction_id + 1) % 0xFFFF

                request = JM38460x44Async.build_request(
                    tid=self.transaction_id,
                    frame_size=self.frame_size,
                    total_frames=self.total_frames
                )

                self.writer.write(request)
                await self.writer.drain()

            except asyncio.TimeoutError:
                print('JM3846 0x44 request timeout')
            except Exception as e:
                print(f'JM3846 0x44 error: {e}')
                await self.async_disconnect()

    async def async_receive_looping_0x44(self):
        """持续接收0x44数据"""
        while self.running:

            try:
                # 检查配置信息
                if any(v is None for v in [self.ch_sel_1, self.ch_sel_0, self.speed_sel]):
                    await self.async_handle_0x03()

                # 接收响应
                response = await asyncio.wait_for(
                    self.reader.read(256),
                    timeout=self.timeout * 2
                )

                # print('=================', response)

                if not response:
                    await asyncio.sleep(2)
                    continue

                res = JM38460x44Async.parse_response(
                    response,
                    ch_sel1=self.ch_sel_1,
                    ch_sel0=self.ch_sel_0,
                    speed_sel=self.speed_sel
                )

                # print('=================', res)

                if res['success']:
                    current_frame = res['current_frame']
                    self.save_0x44_result(res['values'])

                    if current_frame >= self.total_frames:
                        await self.async_handle_0x44()

            except asyncio.TimeoutError:
                print('JM3846 0x44 receive timeout, retrying...')
                await self.async_handle_0x44()
            except ConnectionResetError as e:
                print(f'JM3846 Connection reset: {e}')
                await self.async_disconnect()
                break
            except Exception as e:
                print(f'JM3846 0x44 Receive error: {e}')
                await self.async_disconnect()
                break

    def save_0x44_result(self, result: dict):
        print('result=', result)
        """数据存储方法（保持原逻辑）"""
        if 'ch0_ad' in result:
            ad0 = result['ch0_ad']
            # ad0_mv_per_v = self.jm3846Calculator.calculate_mv_per_v(ad0, self.gain_0)
            microstrain = self.jm3846Calculator.calculate_microstrain(ad0, self.gain_0)
            # torque = self.jm3846Calculator.calculate_torque(ad0, self.gain_0)
            # print(f'ad0={ad0}, ad0_mv_per_v={ad0_mv_per_v}, microstrain={microstrain}, torque={torque}')
        if 'ch1_ad' in result:
            ad1 = result['ch1_ad']
            # ad1_mv_per_v = self.jm3846Calculator.calculate_mv_per_v(ad1, self.gain_1)
            # thrust = self.jm3846Calculator.calculate_thrust(ad1, self.gain_1)
            # print(f'ad1={ad1},ad1_mv_per_v={ad1_mv_per_v},thrust={thrust}')
        if 'rpm' in result:
            rpm = result['rpm'] / 10
            # print('rpm=', rpm)

    async def async_handle_0x45(self):
        """异步处理功能码0x45"""
        async with self._lock:
            try:
                self.transaction_id = (self.transaction_id + 1) % 0xFFFF

                request = JM38460x45Async.build_request(self.transaction_id)
                if not self.writer:
                    return

                self.writer.write(request)
                await self.writer.drain()

                response = await asyncio.wait_for(
                    self.reader.read(256),
                    timeout=self.timeout
                )

                res = JM38460x45Async.parse_response(response)
                print(f'JM3846 0x45 Response: {res}')

            except asyncio.TimeoutError:
                print('JM3846 0x45 request timeout')
            except Exception as e:
                print(f'JM3846 0x45 error: {e}')
                await self.async_disconnect()


jm3846Client: JM3846AsyncClient = JM3846AsyncClient()
