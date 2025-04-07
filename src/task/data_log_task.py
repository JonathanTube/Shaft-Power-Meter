import asyncio
import random
from datetime import datetime

import flet as ft
from db.models.data_log import DataLog
from db.models.propeller_setting import PropellerSetting


class DataLogTask:
    def __init__(self, page: ft.Page):
        self.page = page
        self.is_running = False
        self.update_interval = 1.0  # seconds
        self.get_data()

    def get_data(self):
        propeller_setting = PropellerSetting.get()
        self.max_speed = propeller_setting.rpm_of_mcr_operating_point
        self.max_power = propeller_setting.shaft_power_of_mcr_operating_point

    async def start(self):
        self.is_running = True
        while self.is_running:
            await self.generate_data("sps1")
            await self.generate_data("sps2")
            await asyncio.sleep(self.update_interval)

    def stop(self):
        self.is_running = False

    async def generate_data(self, name):
        # rpm
        speed = random.randint(int(self.max_speed * 0.7), self.max_speed)
        self.__set_session(f"{name}_instant_speed", speed)
        # W
        power = random.randint(int(self.max_power * 0.7), self.max_power)
        self.__set_session(f"{name}_instant_power", power)
        # N
        thrust = random.randint(500, 1000)
        self.__set_session(f"{name}_instant_thrust", thrust)
        # Nm
        torque = random.randint(500, 1000)
        self.__set_session(f"{name}_instant_torque", torque)
        # 圈数
        rounds = int(datetime.now().timestamp())
        self.__set_session(f"{name}_instant_rounds", rounds)
        # 时间
        utc_date_time = self.__get_session('utc_date_time')
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
            self.__set_session(f"{name}_instant_speed", 0)
            self.__set_session(f"{name}_instant_power", 0)
            self.__set_session(f"{name}_instant_thrust", 0)
            self.__set_session(f"{name}_instant_torque", 0)
            self.__set_session(f"{name}_instant_rounds", 0)

    def __set_session(self, key: str, value: any):
        self.page.session.set(key, value)

    def __get_session(self, key: str):
        return self.page.session.get(key)
