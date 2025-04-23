import asyncio

import flet as ft
from pymodbus.client.tcp import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException
from common.const_alarm_type import AlarmType
from common.const_pubsub_topic import PubSubTopic
from db.models.alarm_log import AlarmLog
from db.models.system_settings import SystemSettings
from common.global_data import gdata


class Sps2ReadTask:
    def __init__(self, page: ft.Page):
        self.page = page
        self.sps_client = None
        system_settings: SystemSettings = SystemSettings.get()
        self.amount_of_propeller = system_settings.amount_of_propeller

    async def start(self):
        # if the amount of propeller is 1, don't read the data from the sps2 device
        if self.amount_of_propeller == 1:
            return
        await self.__connect()
        while True:
            # if the test mode is running, don't read the data from the sps device
            if not gdata.test_mode_running:
                await self.__read_sps2_data()
            await asyncio.sleep(1)

    async def __read_sps2_data(self):
        thrust = 0
        torque = 0
        try:
            # get torque
            torque_result = await self.sps_client.read_holding_registers(address=10000)
            if not torque_result.isError():
                value_for_torque = torque_result.registers[0]

            # get thrust
            thrust_result = await self.sps_client.read_holding_registers(address=10001)
            if not thrust_result.isError():
                value_for_thrust = thrust_result.registers[0]

            msg = f"value_for_thrust: {value_for_thrust}, value_for_torque: {value_for_torque}"
            self.__send_msg(msg)

            # TODO: 需要根据实际的传感器类型进行转换
            thrust = value_for_thrust
            torque = value_for_torque

        except ConnectionException as e:
            self.__send_msg(f"Connection error: {e}")
            await self.__connect()
        except Exception as e:
            self.__send_msg(f"Error getting data: {e}")
        finally:
            gdata.sps2_thrust = thrust
            gdata.sps2_torque = torque

    async def __connect(self):
        try:
            if self.sps_client is None:
                self.sps_client = AsyncModbusTcpClient(
                    host=gdata.sps2_ip,
                    port=gdata.sps2_port,
                    timeout=10,
                    retries=3
                )
            is_connected = await self.sps_client.connect()
            self.__send_msg(f"connected to sps: {is_connected}")
            if not is_connected:
                self.__create_alarm_log()
        except Exception as e:
            self.__create_alarm_log()
            self.__send_msg(f"Error connecting to sps: {e}")

    def __create_alarm_log(self):
        cnt: int = AlarmLog.select().where((AlarmLog.alarm_type == AlarmType.SPS2_DISCONNECTED) & (AlarmLog.acknowledge_time == None)).count()

        if cnt == 0:
            AlarmLog.create(
                utc_date_time=gdata.utc_date_time,
                alarm_type=AlarmType.SPS2_DISCONNECTED,
            )

    def __send_msg(self, message: str):
        self.page.pubsub.send_all_on_topic(
            PubSubTopic.TRACE_SPS_LOG, message)
