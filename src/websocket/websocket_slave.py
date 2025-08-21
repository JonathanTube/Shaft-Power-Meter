import asyncio
import websockets
import logging
import msgpack
from peewee import fn
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from db.models.propeller_setting import PropellerSetting
from utils.alarm_saver import AlarmSaver
from playhouse.shortcuts import dict_to_model
from common.global_data import gdata
from utils.datetime_util import DateTimeUtil


class WebSocketSlave:
    def __init__(self):
        self._lock = asyncio.Lock()
        self.websocket = None
        self.is_online = False  # 当前连接是否建立成功
        self.is_canceled = False

    async def start(self):
        """启动客户端（无限重连）"""
        async with self._lock:
            if self.is_online:
                return
            self.is_canceled = False

        while not gdata.configCommon.is_master and not self.is_canceled:
            try:
                ip = gdata.configIO.hmi_server_ip
                port = gdata.configIO.hmi_server_port
                uri = f"ws://{ip}:{port}"
                self.websocket = await websockets.connect(uri)
                self.set_online()
                logging.info(f"[Slave] 已连接到 {uri}")
                await self.receive_data_from_master()
            except Exception as e:
                logging.error(f"[Slave] 连接失败: {e}")
                self.set_offline()
                await asyncio.sleep(10)

    def set_online(self):
        self.is_online = True
        AlarmSaver.recovery(AlarmType.SLAVE_MASTER)

    def set_offline(self):
        self.is_online = False
        AlarmSaver.create(AlarmType.SLAVE_MASTER, True)

    async def send_eexi_breach_alarm_to_master(self, occured):
        if not (self.is_online and not gdata.configCommon.is_master):
            return
        try:
            eexi_breach_msg = {
                "type": "eexi_breach",
                "data": occured
            }
            await self.websocket.send(msgpack.packb(eexi_breach_msg))
        except:
            logging.error("[Slave] send_eexi_breach_alarm_to_master error")

    async def receive_data_from_master(self):
        try:
            async for raw_data in self.websocket:
                receive_data = msgpack.unpackb(raw_data)
                type = receive_data['type']
                if type == 'sps':
                    self._handle_sps_data(receive_data['data'])
                elif type == 'sps2':
                    self._handle_sps2_data(receive_data['data'])
                elif type == 'alarms':
                    await self._handle_alarm(receive_data['data'])
                elif type == 'propeller_setting':
                    dict_to_model(PropellerSetting, receive_data['data']).save()
        except (websockets.ConnectionClosed, websockets.ConnectionClosedError, websockets.ConnectionClosedOK):
            logging.error("[Slave] 连接断开")
            self.set_offline()
        except:
            logging.exception("[Slave] 接收数据异常")
            self.set_offline()

    def _handle_sps_data(self, data):
        if gdata.configTest.test_mode_running:
            # logging.info('[Slave] 测试模式运行中，跳过SPS数据处理')
            return
        gdata.configSPS.torque = data['torque']
        gdata.configSPS.thrust = data['thrust']
        gdata.configSPS.speed = data['speed']
        gdata.configGps.location = data['gps']

    def _handle_sps2_data(self, data):
        if gdata.configTest.test_mode_running:
            # logging.info('[Slave] 测试模式运行中，跳过SPS数据处理')
            return
        gdata.configSPS2.torque = data['torque']
        gdata.configSPS2.thrust = data['thrust']
        gdata.configSPS2.speed = data['speed']
        # 这里gps不处理了，sps已经处理过一次了
        # gdata.configGps.location = data['gps']

    async def _handle_alarm(self, data):
        for alarm in data:
            cnt = AlarmLog.select(fn.COUNT(AlarmLog.id)).where(AlarmLog.alarm_uuid == alarm['alarm_uuid']).scalar()
            if cnt > 0:
                AlarmLog.update(
                    recovery_time=DateTimeUtil.parse_date(alarm['recovery_time']),
                    acknowledge_time=DateTimeUtil.parse_date(alarm['acknowledge_time'])
                ).where(AlarmLog.alarm_uuid == alarm['alarm_uuid']).execute()
            else:
                AlarmLog.create(
                    alarm_uuid=alarm['alarm_uuid'],
                    alarm_type=alarm['alarm_type'],
                    occured_time=DateTimeUtil.parse_date(alarm['occured_time']),
                    recovery_time=DateTimeUtil.parse_date(alarm['recovery_time']),
                    acknowledge_time=DateTimeUtil.parse_date(alarm['acknowledge_time']),
                    out_of_sync=True
                )
            # 每条处理完毕，需要回复服务器
            await self.ack_alarm(alarm['alarm_uuid'])
            # 刷新全局变量
            gdata.configAlarm.set_default_value()

    async def ack_alarm(self, alarm_uuid):
        """发送告警处理确认"""
        try:
            ack_msg = {
                "type": "alarm_ack",
                "data": alarm_uuid
            }
            # 发送 msgpack 格式数据
            if self.websocket and self.is_online:
                await self.websocket.send(msgpack.packb(ack_msg))
        except Exception as e:
            logging.error(f"[Slave] 发送告警确认失败 {alarm_uuid}: {e}")

    async def stop(self):
        self.is_canceled = True
        if not self.is_online:
            return
        try:
            await self.websocket.close()
        except:
            logging.error("[Slave] 关闭连接失败")
        finally:
            self.set_offline()


ws_client = WebSocketSlave()
