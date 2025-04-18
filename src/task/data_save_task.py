import asyncio
import flet as ft
from db.models.data_log import DataLog
from utils.formula_cal import FormulaCalculator
from task.utc_timer_task import utc_timer

class DataSaveTask:
    def __init__(self, page: ft.Page):
        self.page = page
        self.__set_session('sps1_instant_power', 0)
        self.__set_session('sps1_instant_speed', 0)
        self.__set_session('sps1_instant_thrust', 0)
        self.__set_session('sps1_instant_torque', 0)
        self.__set_session('sps1_instant_rounds', 0)

        self.__set_session('sps2_instant_power', 0)
        self.__set_session('sps2_instant_speed', 0)
        self.__set_session('sps2_instant_thrust', 0)
        self.__set_session('sps2_instant_torque', 0)
        self.__set_session('sps2_instant_rounds', 0)

    async def start(self):
        while True:
            await self.save_data('sps1')
            await asyncio.sleep(1)

    async def save_data(self, name: str):
        utc_date_time = utc_timer.get_utc_date_time()
        speed = self.__get_session(f'{name}_instant_speed')

        thrust = self.__get_session(f'{name}_instant_thrust')
        torque = self.__get_session(f'{name}_instant_torque')
        rounds = self.__get_session(f'{name}_instant_rounds')

        power = FormulaCalculator.calculate_instant_power(torque, speed)
        self.__set_session(f'{name}_instant_power', power)

        try:
            DataLog.create(
                utc_date_time=utc_date_time,
                name=name,
                speed=speed,
                power=power,
                thrust=thrust,
                torque=torque,
                rounds=rounds
            )
        except Exception as e:
            print(f"Error generating data: {e}")

    def __get_session(self, key: str):
        return self.page.session.get(key)

    def __set_session(self, key: str, value: any):
        self.page.session.set(key, value)
