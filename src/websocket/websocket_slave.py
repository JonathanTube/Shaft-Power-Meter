
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
from utils.alarm_saver import AlarmSaver
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

    @property
    def is_connected(self):
        return self._is_connected

    async def connect(self):
        async with self._lock:  # 确保单线程重连
            self._retry = 0
            if self._is_connected:
                return

            self._is_canceled = False

            while not gdata.configCommon.is_master and self._retry < self._max_retries:
                # 如果是手动取消，直接跳出
                if self._is_canceled:
                    break

                try:
                    io_conf: IOConf = IOConf.get()
                    uri = f"ws://{io_conf.hmi_server_ip}:{io_conf.hmi_server_port}"
                    self.websocket = await websockets.connect(uri)
                    logging.info(f"[***HMI client***] connected to {uri}")

                    self._is_connected = True
                    AlarmSaver.recovery(AlarmType.SLAVE_CLIENT)

                    # 定期检查gps,alarm,并发送给master
                    asyncio.create_task(self.send_gps_alarm_to_master())

                    # 启动后台接收任务，loop
                    await self.receive_data_from_master()

                    logging.info(f"[***HMI client***] disconnected from {uri}")
                except:
                    logging.error(f"[***HMI client***] failed to connect to {uri}")
                    self._is_connected = False
                    AlarmSaver.create(AlarmType.SLAVE_CLIENT)
                finally:
                    #  指数退避
                    await asyncio.sleep(2 ** self._retry)
                    self._retry += 1

            # 执行到这了，说明已经退出了
            self._is_canceled = False

    async def send_eexi_breach_alarm_to_master(self, occured):
        if gdata.configCommon.is_master:
            return
        if not self._is_connected:
            return
        # 序列化数据
        packed_data = msgpack.packb({
            'type': 'alarm_eexi_breach',
            'data': occured
        })
        await self.websocket.send(packed_data)

    async def send_gps_alarm_to_master(self):
        while not gdata.configCommon.is_master and self._is_connected:
            try:
                alarm_logs: list[AlarmLog] = AlarmLog.select(
                    AlarmLog.id,
                    AlarmLog.alarm_type,
                    AlarmLog.is_recovery,
                    AlarmLog.utc_date_time,
                    AlarmLog.acknowledge_time
                ).where(
                    AlarmLog.is_sync == False,
                    AlarmLog.is_from_master == False,
                    # 彼此的连接错误不同步
                    AlarmLog.alarm_type != AlarmType.SLAVE_CLIENT
                )
                alarm_logs_dict = []
                for alarm_log in alarm_logs:
                    alarm_logs_dict.append({
                        'id': alarm_log.id,
                        'alarm_type': alarm_log.alarm_type,
                        'is_recovery': 1 if alarm_log.is_recovery else 0,
                        'utc_date_time': alarm_log.utc_date_time.strftime(date_time_format) if alarm_log.utc_date_time else "",
                        'acknowledge_time': alarm_log.acknowledge_time.strftime(date_time_format) if alarm_log.acknowledge_time else ""
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
        while not gdata.configCommon.is_master and self._is_connected:

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

                gdata.configSPS.is_offline = False
                gdata.configSPS2.is_offline = False
                self._retry = 0
            except (websockets.ConnectionClosedError, websockets.ConnectionClosedOK, websockets.ConnectionClosed):
                logging.error("[***HMI client***] ConnectionClosedError")
                gdata.configSPS.is_offline = True
                gdata.configSPS2.is_offline = True
                self._is_connected = False
                AlarmSaver.create(AlarmType.SLAVE_CLIENT)
                break
            except:
                logging.exception("[***HMI client***] exception occured at _receive_loop")

    def __handle_jm3846_data(self, data):
        """处理从服务端接收到的数据"""
        if gdata.configTest.test_mode_running:
            logging.info('[***HMI client***] test mode is running, skip handle jm3846 data from websocket.')
            return

        name = data['name']

        if 'torque' in data:
            if name == 'sps':
                gdata.configSPS.torque = data['torque']
            elif name == 'sps2':
                gdata.configSPS2.sps2_torque = data['torque']

        if 'thrust' in data:
            if name == 'sps':
                gdata.configSPS.thrust = data['thrust']
            elif name == 'sps2':
                gdata.configSPS2.sps2_thrust = data['thrust']

        if 'rpm' in data:
            if name == 'sps':
                gdata.configSPS.speed = data['rpm']
            elif name == 'sps2':
                gdata.configSPS2.sps2_speed = data['rpm']

    def __handle_propeller_setting(self, settings):
        data = settings['data']
        model: PropellerSetting = dict_to_model(PropellerSetting, data)
        model.save()

    def __handle_alarm_logs_from_master(self, data):
        """处理alarm数据"""
        alarm_logs = data['data']
        for alarm_log in alarm_logs:
            outer_id = alarm_log['id']
            alarm_type = alarm_log['alarm_type']
            is_recovery = alarm_log['is_recovery']
            utc_date_time = alarm_log['utc_date_time']
            acknowledge_time = alarm_log['acknowledge_time']

            ack_time = None
            if acknowledge_time:
                ack_time = datetime.strptime(acknowledge_time, date_time_format)

            udt = None
            if utc_date_time:
                udt = datetime.strptime(utc_date_time, date_time_format)

            # 查找是否存在
            cnt = AlarmLog.select().where(AlarmLog.out_id == outer_id).count()

            if cnt > 0:
                AlarmLog.update(acknowledge_time=ack_time).where(AlarmLog.out_id == outer_id).execute()
            else:
                AlarmLog.create(
                    utc_date_time=udt, acknowledge_time=ack_time,
                    alarm_type=alarm_type, is_recovery=is_recovery,
                    is_from_master=True, outer_id=outer_id
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


ws_client = WebSocketSlave()
