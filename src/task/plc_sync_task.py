import asyncio
import flet as ft
from pymodbus.client.tcp import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException
from common.const_alarm_type import AlarmType
from common.const_pubsub_topic import PubSubTopic
from db.models.io_conf import IOConf
from db.models.alarm_log import AlarmLog
from common.global_data import gdata
from task.utc_timer_task import utc_timer


class PlcSyncTask:
    def __init__(self, page: ft.Page):
        self.page = page
        self.plc_client = None
        self.io_conf = IOConf.get()

    async def start(self):
        await self.__connect()
        while True:
            try:
                await self.__read_data()
                await self.__write_data()
            except ConnectionException as e:
                self.__send_msg(f"Connection error: {e}")
                self.__create_alarm_log()
                await self.__connect()
            except Exception as e:
                self.__send_msg(f"Error: {e}")
            await asyncio.sleep(1)

    async def __get_data(self, address: int):
        result = await self.plc_client.read_holding_registers(address=address)
        if not result.isError():
            return result.registers[0]
        return None

    async def __read_data(self):
        speed = 0
        rounds = 0

        # 4-20MA对应-功率-下限
        power_range_min = await self.__get_data(12298)
        # 4-20MA对应-功率-上限
        power_range_max = await self.__get_data(12299)
        # 4-20MA对应-功率-偏移
        power_range_offset = await self.__get_data(12300)
        # get power
        power = await self.__get_data(12301)

        # 4-20MA对应-扭矩-下限
        torque_range_min = await self.__get_data(12308)
        # 4-20MA对应-扭矩-上限
        torque_range_max = await self.__get_data(12309)
        # 4-20MA对应-扭矩-偏移
        torque_range_offset = await self.__get_data(12310)
        # get torque
        torque = await self.__get_data(12302)

        # 4-20MA对应-推力-下限
        thrust_range_min = await self.__get_data(12318)
        # 4-20MA对应-推力-上限
        thrust_range_max = await self.__get_data(12319)
        # 4-20MA对应-推力-偏移
        thrust_range_offset = await self.__get_data(12320)
        # get thrust
        thrust = await self.__get_data(12303)

        # 4-20MA对应-转速-下限
        speed_range_min = await self.__get_data(12328)
        # 4-20MA对应-转速-上限
        speed_range_max = await self.__get_data(12329)
        # 4-20MA对应-转速-偏移
        speed_range_offset = await self.__get_data(12330)
        # get speed
        speed = await self.__get_data(12332)
        # get rounds
        rounds = await self.__get_data(12333)

        msg_range_power = f"4-20MA power (min:{power_range_min}, max:{power_range_max}, offset:{power_range_offset})"
        msg_range_torque = f"4-20MA torque (min:{torque_range_min}, max:{torque_range_max}, offset:{torque_range_offset})"
        msg_range_thrust = f"4-20MA thrust (min:{thrust_range_min}, max:{thrust_range_max}, offset:{thrust_range_offset})"
        msg_range_speed = f"4-20MA speed (min:{speed_range_min}, max:{speed_range_max}, offset:{speed_range_offset})"
        msg_instant_values = f"instant values: power:{power}, torque:{torque}, thrust:{thrust}, speed:{speed}, rounds:{rounds}"
        self.__send_msg(
            f"[{msg_range_power}] , [{msg_range_torque}] , [{msg_range_thrust}] , [{msg_range_speed}] , [{msg_instant_values}]")

        gdata.sps1_speed = speed
        gdata.sps1_rounds = rounds

    async def __write_data(self):
        # 写入功率
        power = int(gdata.sps1_power/1000)
        self.plc_client.write_register(12301, power)
        # 写入扭矩
        torque = int(gdata.sps1_torque/1000)
        self.plc_client.write_register(12302, torque)
        # 写入推力
        thrust = int(gdata.sps1_thrust/1000)
        self.plc_client.write_register(12303, thrust)

    async def __connect(self):
        try:
            if self.plc_client is None:
                self.plc_client = AsyncModbusTcpClient(
                    host=self.io_conf.plc_ip,
                    port=self.io_conf.plc_port,
                    timeout=10,
                    retries=3
                )
            is_connected = await self.plc_client.connect()
            self.__send_msg(f"connected to PLC: {is_connected}")
            if not is_connected:
                self.__create_alarm_log()
        except Exception as e:
            self.__send_msg(f"Error connecting to PLC: {e}")
            self.__create_alarm_log()

    def __set_session(self, key: str, value: any):
        self.page.session.set(key, value)

    def __send_msg(self, message: str):
        self.page.pubsub.send_all_on_topic(PubSubTopic.TRACE_PLC_LOG, message)

    def __create_alarm_log(self):
        cnt: int = AlarmLog.select().where(
            (AlarmLog.alarm_type == AlarmType.PLC_DISCONNECTED) & (
                AlarmLog.acknowledge_time == None)
        ).count()

        if cnt == 0:
            AlarmLog.create(
                utc_date_time=utc_timer.get_utc_date_time(),
                alarm_type=AlarmType.PLC_DISCONNECTED,
            )
            gdata.alarm_occured = True
