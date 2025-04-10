import asyncio
from datetime import datetime

import flet as ft
from pymodbus.client.tcp import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException


class ModbusReadTask:
    def __init__(self, page: ft.Page):
        self.page = page
        self.modbus_client = None

    async def start(self):
        await self.__connect()
        while True:
            await self.__read_sps1_data()
            await self.__read_sps2_data()
            await asyncio.sleep(1)

    async def __read_sps1_data(self):
        thrust = 0
        torque = 0
        try:
            # get torque
            torque_result = await self.modbus_client.read_holding_registers(address=10000)
            if not torque_result.isError():
                value_for_torque = torque_result.registers[0]

            # get thrust
            thrust_result = await self.modbus_client.read_holding_registers(address=10001)
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
            print(f"Error getting data: {e}")
            self.__send_msg(f"Error getting data: {e}")
        finally:
            self.__set_session('sps1_instant_thrust', thrust)
            self.__set_session('sps1_instant_torque', torque)

    async def __read_sps2_data(self):
        pass

    async def __connect(self):
        try:
            self.modbus_client = AsyncModbusTcpClient(
                host="127.0.0.1", port=503)
            is_connected = await self.modbus_client.connect()
            self.__send_msg(f"connected to Modbus: {is_connected}")
        except Exception as e:
            self.__send_msg(f"Error connecting to Modbus: {e}")

    def __set_session(self, key: str, value: any):
        self.page.session.set(key, value)

    def __send_msg(self, message: str):
        self.page.pubsub.send_all_on_topic('modbus_log', message)
