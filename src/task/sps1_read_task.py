import asyncio
import logging
import flet as ft
from pymodbus.client.tcp import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException
from common.const_alarm_type import AlarmType
from common.global_data import gdata
from utils.alarm_saver import AlarmSaver


class Sps1ReadTask:
    def __init__(self, page: ft.Page):
        self.page = page
        self.sps_client = None

    async def start(self):
        await self.__connect()
        while True:
            # if the test mode is running, don't read the data from the sps device
            if not gdata.test_mode_running:
                await self.__read_sps1_data()
            await asyncio.sleep(1)

    async def __read_sps1_data(self):
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
            logging.error(f"sps1 read task connection error: {e}")
            self.__send_msg(f"Connection error: {e}")
            await self.__connect()
        except Exception as e:
            logging.error(f"sps1 read task error: {e}")
            self.__send_msg(f"Error getting data: {e}")
        finally:
            gdata.sps1_thrust = thrust
            gdata.sps1_torque = torque

    async def __connect(self):
        try:
            if self.sps_client is None:
                self.sps_client = AsyncModbusTcpClient(
                    host=gdata.sps1_ip,
                    port=gdata.sps1_port,
                    timeout=10,
                    retries=3
                )
            is_connected = await self.sps_client.connect()
            self.__send_msg(f"connected to sps: {is_connected}")
            if not is_connected:
                AlarmSaver.create(AlarmType.SPS1_DISCONNECTED)
        except Exception as e:
            logging.error(f"sps1 read task connect error: {e}")
            AlarmSaver.create(AlarmType.SPS1_DISCONNECTED)
            self.__send_msg(f"Error connecting to sps: {e}")
