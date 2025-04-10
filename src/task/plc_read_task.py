import asyncio

import flet as ft
from pymodbus.client.tcp import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException


class PlcReadTask:
    def __init__(self, page: ft.Page):
        self.page = page
        self.plc_client = None

    async def start(self):
        await self.__connect()
        while True:
            await self.__read_sps1_data()
            await self.__read_sps2_data()
            await asyncio.sleep(1)

    async def __read_sps1_data(self):
        speed = 0
        rounds = 0
        try:
            # get speed
            result_speed = await self.plc_client.read_holding_registers(address=12332)
            if not result_speed.isError():
                speed = result_speed.registers[0]
            # get rounds
            result_rounds = await self.plc_client.read_holding_registers(address=12333)
            if not result_rounds.isError():
                rounds = result_rounds.registers[0]
            self.__send_msg(f"speed: {speed}, rounds: {rounds}")
        except ConnectionException as e:
            self.__send_msg(f"Connection error: {e}")
            await self.__connect()
        except Exception as e:
            print(f"Error getting data: {e}")
            self.__send_msg(f"Error getting data: {e}")
        finally:
            self.__set_session('sps1_instant_speed', speed)
            self.__set_session('sps1_instant_rounds', rounds)

    async def __read_sps2_data(self):
        pass

    async def __connect(self):
        try:
            self.plc_client = AsyncModbusTcpClient(host="127.0.0.1", port=502)
            is_connected = await self.plc_client.connect()
            self.__send_msg(f"connected to PLC: {is_connected}")
        except Exception as e:
            self.__send_msg(f"Error connecting to PLC: {e}")

    def __set_session(self, key: str, value: any):
        self.page.session.set(key, value)

    def __send_msg(self, message: str):
        self.page.pubsub.send_all_on_topic('plc_log', message)
