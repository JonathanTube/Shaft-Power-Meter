
# ====================== 客户端类 ======================
import asyncio
from datetime import datetime
import websockets
import logging
import msgpack
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from db.models.io_conf import IOConf
from db.models.propeller_setting import PropellerSetting
from jm3846.JM3846_calculator import JM3846Calculator
from utils.alarm_saver import AlarmSaver
from utils.data_saver import DataSaver
from playhouse.shortcuts import dict_to_model
from common.global_data import gdata


date_time_format = '%Y-%m-%d %H:%M:%S'


class WebSocketSlave:
    def __init__(self):
        self._lock = asyncio.Lock()

        self.websocket = None

        self._retry = 0

        self._is_connected = False

        self._is_canceled = False

        self._max_retries = 6  # 最大重连次数

        self.jm3846Calculator = JM3846Calculator()

    @property
    def is_connected(self):
        return self._is_connected

    async def connect(self):
        async with self._lock:  # 确保单线程重连
            if self._is_connected:
                return

            self._is_canceled = False

            while not gdata.is_master and self._retry < self._max_retries:
                # 如果是手动取消，直接跳出
                if self._is_canceled:
                    break

                try:
                    io_conf: IOConf = IOConf.get()
                    uri = f"ws://{io_conf.hmi_server_ip}:{io_conf.hmi_server_port}"
                    self.websocket = await websockets.connect(uri)
                    logging.info(f"[***HMI client***] connected to {uri}")

                    self._is_connected = True
                    AlarmSaver.recovery(alarm_type=AlarmType.SLAVE_CLIENT_DISCONNECTED)

                    # 定期检查gps,alarm,并发送给master
                    asyncio.create_task(self.send_gps_alarm_to_master())

                    # 启动后台接收任务，loop
                    await self.receive_data_from_master()

                    logging.info(f"[***HMI client***] disconnected from {uri}")
                except:
                    logging.error(f"[***HMI client***] failed to connect to {uri}")
                    self._is_connected = False
                    AlarmSaver.create(alarm_type=AlarmType.SLAVE_CLIENT_DISCONNECTED)
                finally:
                    #  指数退避
                    await asyncio.sleep(2 ** self._retry)
                    self._retry += 1

            # 执行到这了，说明已经退出了
            self._is_canceled = False

    async def send_gps_alarm_to_master(self):
        while not gdata.is_master and self._is_connected:
            try:
                alarm_logs: list[AlarmLog] = AlarmLog.select(
                    AlarmLog.id,
                    AlarmLog.alarm_type,
                    AlarmLog.is_recovery,
                    AlarmLog.acknowledge_time
                ).where(
                    AlarmLog.alarm_type == AlarmType.SLAVE_GPS_DISCONNECTED,
                    AlarmLog.is_sync == False
                )
                alarm_logs_dict = []
                for alarm_log in alarm_logs:
                    alarm_logs_dict.append({
                        'alarm_type': alarm_log.alarm_type,
                        'acknowledge_time': alarm_log.acknowledge_time.strftime(date_time_format) if alarm_log.acknowledge_time else "",
                        'is_recovery': 1 if alarm_log.is_recovery else 0
                    })
                if len(alarm_logs) > 0:
                    # 序列化数据
                    packed_data = msgpack.packb({
                        'type': 'alarm_logs_from_slave',
                        'data': alarm_logs_dict
                    })
                    await self.websocket.send(packed_data)
                    for alarm_log in alarm_logs:
                        AlarmLog.update(is_sync=True).where(AlarmLog.id == alarm_log.id).execute()
            except:
                logging.error("[***HMI client***] send_gps_alarm_to_master error")
            finally:
                await asyncio.sleep(5)

    async def receive_data_from_master(self):
        while not gdata.is_master and self._is_connected:

            if self._is_canceled:
                return

            try:
                raw_data = await self.websocket.recv()
                data = msgpack.unpackb(raw_data)

                if data['type'] == 'sps_data':
                    self.__handle_jm3846_data(data)
                elif data['type'] == 'alarm_logs_from_master':
                    self.__handle_alarm_logs_from_master(data)
                elif data['type'] == 'propeller_setting':
                    self.__handle_propeller_setting(data)

                gdata.sps1_offline = False
                gdata.sps2_offline = False
                self._retry = 0
            except (websockets.ConnectionClosedError,
                    websockets.ConnectionClosedOK,
                    websockets.ConnectionClosed):
                logging.error("[***HMI client***] ConnectionClosedError")
                gdata.sps1_offline = True
                gdata.sps2_offline = True
                self._is_connected = False
                AlarmSaver.create(alarm_type=AlarmType.SLAVE_CLIENT_DISCONNECTED)
                break
            except:
                logging.exception("[***HMI client***] exception occured at _receive_loop")

    def __handle_jm3846_data(self, data):
        """处理从服务端接收到的数据"""
        if gdata.test_mode_running:
            logging.info('[***HMI client***] test mode is running, skip handle jm3846 data from websocket.')
            return

        name = data['name']
        ad0_torque = 0
        ad1_thrust = 0
        speed = 0

        if 'torque' in data:
            ad0_torque = data['torque']
        if 'thrust' in data:
            ad1_thrust = data['thrust']
        if 'rpm' in data:
            speed = data['rpm']

        DataSaver.save(name, ad0_torque, ad1_thrust, speed)

    def __handle_propeller_setting(self, settings):
        data = settings['data']
        model: PropellerSetting = dict_to_model(PropellerSetting, data)
        model.save()

    def __handle_alarm_logs_from_master(self, data):
        """处理alarm数据"""
        alarm_logs = data['data']
        for alarm_log in alarm_logs:
            alarm_type = alarm_log['alarm_type']
            acknowledge_time = alarm_log['acknowledge_time']

            ack_time = None
            if acknowledge_time:
                ack_time = datetime.strptime(acknowledge_time, date_time_format)

            is_recovery = alarm_log['is_recovery']
            if is_recovery == 1:
                AlarmLog.update(
                    is_recovery=True, acknowledge_time=ack_time
                ).where(
                    AlarmLog.is_from_master == True, AlarmLog.alarm_type == alarm_type
                ).execute()
            else:
                cnt: int = AlarmLog.select().where(
                    AlarmLog.is_from_master == True,
                    AlarmLog.alarm_type == alarm_type,
                    AlarmLog.is_recovery == False
                ).count()
                if cnt == 0:
                    AlarmLog.create(
                        utc_date_time=gdata.utc_date_time,
                        acknowledge_time=ack_time,
                        is_from_master=True,
                        alarm_type=alarm_type
                    )

    async def close(self):
        self._is_canceled = True

        if not self._is_connected:
            return

        try:
            if self.websocket:
                await self.websocket.close()
                await self.websocket.wait_closed()
        except:
            logging.error("[***HMI client***] failed to close websocket connection")
        finally:
            self._is_connected = False
            AlarmSaver.create(alarm_type=AlarmType.SLAVE_CLIENT_DISCONNECTED)


ws_client = WebSocketSlave()
