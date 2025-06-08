
# ====================== 客户端类 ======================
import asyncio
from datetime import datetime
import websockets
import logging
import msgpack
from common.const_alarm_type import AlarmType
from db.models.io_conf import IOConf
from db.models.zero_cal_info import ZeroCalInfo
from db.models.zero_cal_record import ZeroCalRecord
from jm3846.JM3846_calculator import JM3846Calculator
from utils.alarm_saver import AlarmSaver
from utils.data_saver import DataSaver
from common.global_data import gdata


class WebSocketClient:
    def __init__(self):
        self.websocket = None
        self._running = False
        self.jm3846Calculator = JM3846Calculator()

    async def connect(self):
        """连接服务端"""
        try:
            io_conf: IOConf = IOConf.get()
            uri = f"ws://{io_conf.hmi_server_ip}:{io_conf.hmi_server_port}"
            self.websocket = await websockets.connect(uri)
            self._running = True
            logging.info(f"connected to {uri} successfully")
            gdata.connected_to_hmi_server = True
            # 启动后台接收任务
            asyncio.create_task(self._receive_loop())
        except Exception:
            logging.error(f"failed to connect to {uri}")
            self._running = False
            AlarmSaver.create(alarm_type=AlarmType.HMI_CLIENT_DISCONNECTED)
            return False

        return True

    async def _receive_loop(self):
        """持续接收消息的循环"""
        try:
            while self._running:
                raw_data = await self.websocket.recv()
                data = msgpack.unpackb(raw_data)
                logging.info(f"client received: {data}")
                if data['type'] == 'sps_data':
                    self.__handle_jm3846_data(data)
                elif data['type'] == 'zero_cal':
                    self.__handle_zero_cal(data)
                gdata.sps1_offline = False
                gdata.sps2_offline = False
        except websockets.ConnectionClosed:
            logging.exception("server connection closed")
            self._running = False
            gdata.connected_to_hmi_server = False
            AlarmSaver.create(alarm_type=AlarmType.HMI_CLIENT_DISCONNECTED)
            gdata.sps1_offline = True
            gdata.sps2_offline = True
            await self.connect()

    async def send(self, data):
        """向服务端发送数据"""
        if self.websocket:
            packed_data = msgpack.packb(data)
            await self.websocket.send(packed_data)
            return True
        return False

    def __handle_jm3846_data(self, data):
        """处理从服务端接收到的数据"""
        if gdata.test_mode_running:
            logging.info('test mode is running, skip handle jm3846 data from websocket.')
            return

        name = data['name']
        ad0_torque = 0
        ad1_thrust = 0
        speed = 0

        if 'torque' in data:
            ad0_torque = data['torque']
        if 'ch1_ad' in data:
            ad1_thrust = data['thrust']
        if 'rpm' in data:
            speed = data['rpm'] / 10

        DataSaver.save(name, ad0_torque, ad1_thrust, speed)

    def __handle_zero_cal(self, data):
        """处理零点校准数据"""
        id = data['id']
        zero_cal_info: ZeroCalInfo = ZeroCalInfo.get_or_none(ZeroCalInfo.id == id)
        if zero_cal_info is not None:
            zero_cal_info.delete_instance()

        new_zero_cal_info = ZeroCalInfo.create(
            id=data['id'],
            name=data['name'],
            utc_date_time=datetime.strptime(data['utc_date_time'], '%Y-%m-%d %H:%M:%S'),
            torque_offset=data['torque_offset'],
            thrust_offset=data['thrust_offset'],
            state=data['state']
        )

        for record in data['records']:
            ZeroCalRecord.create(
                zero_cal_info=new_zero_cal_info,
                name=record['name'],
                mv_per_v_for_torque=record['mv_per_v_for_torque'],
                mv_per_v_for_thrust=record['mv_per_v_for_thrust'],
            )

        if data['state'] == 1:
            if data['name'] == 'sps1':
                gdata.sps1_torque_offset = data['torque_offset']
                gdata.sps1_thrust_offset = data['thrust_offset']
            elif data['name'] == 'sps2':
                gdata.sps2_torque_offset = data['torque_offset']
                gdata.sps2_thrust_offset = data['thrust_offset']

    async def close(self):
        """关闭连接"""
        try:
            self._running = False
            if self.websocket:
                await self.websocket.close()
                AlarmSaver.create(alarm_type=AlarmType.HMI_SERVER_CLOSED)
        except Exception:
            logging.exception("failed to close websocket connection")
            return False
        return True


ws_client = WebSocketClient()
# # 客户端消息处理器
# def client_message_handler(data):
#     print(f"客户端处理消息: {data}")

# async def main_client():
#     client = WebSocketClient("ws://localhost:8765")
#     client.set_message_handler(client_message_handler)
#     await client.connect()

#     # 客户端主动发送消息（每3秒一次）
#     counter = 0
#     while True:
#         await client.send('hello world')
#         counter += 1
#         await asyncio.sleep(3)

# # 启动客户端
# asyncio.run(main_client())
