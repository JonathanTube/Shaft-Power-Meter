import asyncio

import flet as ft
from pymodbus.client.tcp import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException

from db.models.io_conf import IOConf


class PlcReadTask:
    def __init__(self, page: ft.Page):
        self.page = page
        self.plc_client = None
        self.io_conf = IOConf.get()

    async def start(self):
        await self.__connect()
        while True:
            await self.__read_sps1_data()
            await self.__read_sps2_data()
            self.__write_sps1_data()
            self.__write_sps2_data()
            await asyncio.sleep(1)

    async def __read_sps1_data(self):
        speed = 0
        rounds = 0
        try:
            # 4-20MA对应-功率-下限
            result_power_range_min = await self.plc_client.read_holding_registers(address=12298)
            if not result_power_range_min.isError():
                power_range_min = result_power_range_min.registers[0]
            # 4-20MA对应-功率-上限
            result_power_range_max = await self.plc_client.read_holding_registers(address=12299)
            if not result_power_range_max.isError():
                power_range_max = result_power_range_max.registers[0]
            # 4-20MA对应-功率-偏移
            result_power_range_offset = await self.plc_client.read_holding_registers(address=12300)
            if not result_power_range_offset.isError():
                power_range_offset = result_power_range_offset.registers[0]
            # get power
            result_power = await self.plc_client.read_holding_registers(address=12301)
            if not result_power.isError():
                power = result_power.registers[0]


            # 4-20MA对应-扭矩-下限
            result_torque_range_min = await self.plc_client.read_holding_registers(address=12308)
            if not result_torque_range_min.isError():
                torque_range_min = result_torque_range_min.registers[0]
            # 4-20MA对应-扭矩-上限
            result_torque_range_max = await self.plc_client.read_holding_registers(address=12309)
            if not result_torque_range_max.isError():
                torque_range_max = result_torque_range_max.registers[0]
            # 4-20MA对应-扭矩-偏移
            result_torque_range_offset = await self.plc_client.read_holding_registers(address=12310)
            if not result_torque_range_offset.isError():
                torque_range_offset = result_torque_range_offset.registers[0]
            # get torque
            result_torque = await self.plc_client.read_holding_registers(address=12302)
            if not result_torque.isError():
                torque = result_torque.registers[0]


            # 4-20MA对应-推力-下限
            result_thrust_range_min = await self.plc_client.read_holding_registers(address=12318)
            if not result_thrust_range_min.isError():
                thrust_range_min = result_thrust_range_min.registers[0]
            # 4-20MA对应-推力-上限
            result_thrust_range_max = await self.plc_client.read_holding_registers(address=12319)
            if not result_thrust_range_max.isError():
                thrust_range_max = result_thrust_range_max.registers[0]
            # 4-20MA对应-推力-偏移
            result_thrust_range_offset = await self.plc_client.read_holding_registers(address=12320)
            if not result_thrust_range_offset.isError():
                thrust_range_offset = result_thrust_range_offset.registers[0]
            # get thrust
            result_thrust = await self.plc_client.read_holding_registers(address=12303)
            if not result_thrust.isError():
                thrust = result_thrust.registers[0]


            # 4-20MA对应-转速-下限
            result_speed_range_min = await self.plc_client.read_holding_registers(address=12328)
            if not result_speed_range_min.isError():
                speed_range_min = result_speed_range_min.registers[0]
            # 4-20MA对应-转速-上限
            result_speed_range_max = await self.plc_client.read_holding_registers(address=12329)
            if not result_speed_range_max.isError():
                speed_range_max = result_speed_range_max.registers[0]
            # 4-20MA对应-转速-偏移
            result_speed_range_offset = await self.plc_client.read_holding_registers(address=12330)
            if not result_speed_range_offset.isError():
                speed_range_offset = result_speed_range_offset.registers[0]
            # get speed
            result_speed = await self.plc_client.read_holding_registers(address=12332)
            if not result_speed.isError():
                speed = result_speed.registers[0]


            # get rounds
            result_rounds = await self.plc_client.read_holding_registers(address=12333)
            if not result_rounds.isError():
                rounds = result_rounds.registers[0]

            msg_range_power = f"4-20MA power (min:{power_range_min}, max:{power_range_max}, offset:{power_range_offset})"
            msg_range_torque = f"4-20MA torque (min:{torque_range_min}, max:{torque_range_max}, offset:{torque_range_offset})"
            msg_range_thrust = f"4-20MA thrust (min:{thrust_range_min}, max:{thrust_range_max}, offset:{thrust_range_offset})"
            msg_range_speed = f"4-20MA speed (min:{speed_range_min}, max:{speed_range_max}, offset:{speed_range_offset})"
            msg_instant_values = f"instant values: power:{power}, torque:{torque}, thrust:{thrust}, speed:{speed}, rounds:{rounds}"
            self.__send_msg(
                f"[{msg_range_power}] , [{msg_range_torque}] , [{msg_range_thrust}] , [{msg_range_speed}] , [{msg_instant_values}]")

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

    def __write_sps1_data(self):
        try:
            # 写入功率
            power = int(self.page.session.get('sps1_instant_power')/1000)
            self.plc_client.write_register(12301, power)
            # 写入扭矩
            torque = int(self.page.session.get('sps1_instant_torque')/1000)
            self.plc_client.write_register(12302, torque)
            # 写入推力
            thrust = int(self.page.session.get('sps1_instant_thrust')/1000)
            self.plc_client.write_register(12303, thrust)
        except Exception as e:
            self.__send_msg(f"Error writing data: {e}")

    def __write_sps2_data(self):
        pass

    async def __connect(self):
        try:
            self.plc_client = AsyncModbusTcpClient(
                host=self.io_conf.plc_ip, port=self.io_conf.plc_port)
            is_connected = await self.plc_client.connect()
            self.__send_msg(f"connected to PLC: {is_connected}")
        except Exception as e:
            self.__send_msg(f"Error connecting to PLC: {e}")

    def __set_session(self, key: str, value: any):
        self.page.session.set(key, value)

    def __send_msg(self, message: str):
        self.page.pubsub.send_all_on_topic('plc_log', message)
