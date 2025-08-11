import asyncio
import websockets
import logging
import msgpack
from peewee import fn
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from db.models.io_conf import IOConf
from db.models.propeller_setting import PropellerSetting
from utils.alarm_saver import AlarmSaver
from playhouse.shortcuts import dict_to_model
from common.global_data import gdata
from utils.datetime_util import DateTimeUtil


date_time_format = '%Y-%m-%d %H:%M:%S'


class WebSocketSlave:
    def __init__(self):
        self._lock = asyncio.Lock()
        self.websocket = None
        self.is_online = False  # 当前连接状态
        self._is_canceled = False

    async def start(self):
        """启动客户端（无限重连版）"""
        async with self._lock:
            if self.is_online:
                return

            self._is_canceled = False

            while not gdata.configCommon.is_master:
                # 如果是手动取消，直接跳出
                if self._is_canceled:
                    break

                try:
                    io_conf: IOConf = IOConf.get()
                    uri = f"ws://{io_conf.hmi_server_ip}:{io_conf.hmi_server_port}"
                    self.websocket = await websockets.connect(uri)
                    logging.info(f"[Slave客户端] 已连接到 {uri}")

                    self.is_online = True
                    AlarmSaver.recovery(AlarmType.SLAVE_MASTER)

                    # 启动接收 & 发送任务
                    asyncio.create_task(self.send_gps_alarm_to_master())
                    asyncio.create_task(self.receive_data_from_master())

                    return  # 成功连接直接退出重连循环
                except:
                    logging.error(f"[Slave客户端] 连接失败，5 秒后重试")
                    self.is_online = False
                    AlarmSaver.create(AlarmType.SLAVE_MASTER)

                await asyncio.sleep(5)  # 固定重连间隔

    async def send_eexi_breach_alarm_to_master(self, occured):
        if gdata.configCommon.is_master:
            return
        if not self.is_online:
            return
        try:
            packed_data = msgpack.packb({
                'type': 'alarm_eexi_breach',
                'data': occured
            })
            await self.websocket.send(packed_data)
        except:
            logging.error("[Slave客户端] send_eexi_breach_alarm_to_master error")

    async def send_gps_alarm_to_master(self):
        while not gdata.configCommon.is_master and self.is_online:
            try:
                alarm_logs: list[AlarmLog] = AlarmLog.select(
                    AlarmLog.id,
                    AlarmLog.alarm_type,
                    AlarmLog.occured_time,
                    AlarmLog.recovery_time,
                    AlarmLog.acknowledge_time
                ).where(
                    AlarmLog.is_sync == False,
                    AlarmLog.is_from_master == False,
                    AlarmLog.alarm_type != AlarmType.SLAVE_MASTER
                )
                alarm_logs_dict = []
                for alarm_log in alarm_logs:
                    alarm_logs_dict.append({
                        'id': alarm_log.id,
                        'alarm_type': alarm_log.alarm_type,
                        'occured_time': DateTimeUtil.format_date(alarm_log.occured_time),
                        'recovery_time': DateTimeUtil.format_date(alarm_log.recovery_time),
                        'acknowledge_time': DateTimeUtil.format_date(alarm_log.acknowledge_time)
                    })
                if len(alarm_logs) > 0:
                    packed_data = msgpack.packb({
                        'type': 'alarm_logs_from_slave',
                        'data': alarm_logs_dict
                    })
                    await self.websocket.send(packed_data)
                    for alarm_log in alarm_logs:
                        AlarmLog.update(is_sync=True).where(AlarmLog.id == alarm_log.id).execute()
            except:
                logging.error("[Slave客户端] send_gps_alarm_to_master error")
            finally:
                await asyncio.sleep(5)

    async def receive_data_from_master(self):
        while not gdata.configCommon.is_master and self.is_online:
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
            except (websockets.ConnectionClosedError, websockets.ConnectionClosedOK, websockets.ConnectionClosed):
                logging.error("[Slave客户端] 连接断开")
                gdata.configSPS.is_offline = True
                gdata.configSPS2.is_offline = True
                self.is_online = False
                AlarmSaver.create(AlarmType.SLAVE_MASTER)
                break
            except:
                logging.exception("[Slave客户端] 接收数据异常")

    def __handle_jm3846_data(self, data):
        if gdata.configTest.test_mode_running:
            logging.info('[Slave客户端] 测试模式运行中，跳过SPS数据处理')
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
        alarm_logs = data['data']
        for alarm_log in alarm_logs:
            outer_id = alarm_log['id']
            alarm_type = alarm_log['alarm_type']
            occured_time = alarm_log['occured_time']
            recovery_time = alarm_log['recovery_time']
            acknowledge_time = alarm_log['acknowledge_time']

            cnt: int = AlarmLog.select(fn.COUNT(AlarmLog.id)).where(AlarmLog.outer_id == outer_id).scalar()

            if cnt > 0:
                AlarmLog.update(
                    recovery_time=DateTimeUtil.parse_date(recovery_time),
                    acknowledge_time=DateTimeUtil.parse_date(acknowledge_time)
                ).where(AlarmLog.outer_id == outer_id).execute()
            else:
                AlarmLog.create(
                    alarm_type=alarm_type,
                    occured_time=DateTimeUtil.parse_date(occured_time),
                    recovery_time=DateTimeUtil.parse_date(recovery_time),
                    acknowledge_time=DateTimeUtil.parse_date(acknowledge_time),
                    is_from_master=True,
                    outer_id=outer_id
                )

    async def stop(self):
        self._is_canceled = True

        if not self.is_online:
            return

        try:
            if self.websocket:
                await self.websocket.close()
                await self.websocket.wait_closed()
        except:
            logging.error("[Slave客户端] 关闭连接失败")
        finally:
            self.is_online = False


ws_client = WebSocketSlave()