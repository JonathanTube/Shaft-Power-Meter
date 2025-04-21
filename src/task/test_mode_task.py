import flet as ft
import asyncio
import random

from db.models.data_log import DataLog
from db.models.system_settings import SystemSettings
from utils.formula_cal import FormulaCalculator
from common.global_data import gdata
from db.models.alarm_log import AlarmLog
from db.models.event_log import EventLog
from db.models.report_info import ReportInfo
from common.public_controls import PublicControls


class TestModeTask:
    def __init__(self, page: ft.Page):
        self.page = page
        self.min_torque = 0
        self.max_torque = 0
        self.min_speed = 0
        self.max_speed = 0
        self.min_thrust = 0
        self.max_thrust = 0
        self.min_revolution = 0
        self.max_revolution = 0
        self.is_running = False

    def set_torque_range(self, min_torque, max_torque):
        self.min_torque = min_torque
        self.max_torque = max_torque

    def set_speed_range(self, min_speed, max_speed):
        self.min_speed = min_speed
        self.max_speed = max_speed

    def set_thrust_range(self, min_thrust, max_thrust):
        self.min_thrust = min_thrust
        self.max_thrust = max_thrust

    def set_revolution_range(self, min_revolution, max_revolution):
        self.min_revolution = min_revolution
        self.max_revolution = max_revolution

    async def start(self):
        self.system_settings = SystemSettings.get()
        self.is_running = True
        # start a thread to generate random data every seconds
        return asyncio.create_task(self.generate_random_data())

    def stop(self):
        try:
            DataLog.truncate_table()
            AlarmLog.truncate_table()
            EventLog.truncate_table()
            ReportInfo.truncate_table()
            gdata.sps1_speed = 0
            gdata.sps1_power = 0
            gdata.sps1_torque = 0
            gdata.sps1_thrust = 0
            gdata.sps1_rounds = 0

            gdata.sps2_speed = 0
            gdata.sps2_power = 0
            gdata.sps2_torque = 0
            gdata.sps2_thrust = 0
            gdata.sps2_rounds = 0
            PublicControls.on_eexi_power_breach_recovery()
            PublicControls.on_power_overload_recovery()
        except Exception as e:
            print(f'Error truncating DataLog table: {e}')
        self.is_running = False

    async def generate_random_data(self):
        # print(f'self.is_running={self.is_running}')
        while self.is_running:
            # start to generate random data in range of min and max
            # print(f'generate_random_data')
            await self.save_generated_data('sps1')
            if self.system_settings.amount_of_propeller == 2:
                await self.save_generated_data('sps2')
            PublicControls.on_instant_data_refresh()
            await asyncio.sleep(1)

    async def save_generated_data(self, name):
        instant_torque = int(random.uniform(self.min_torque, self.max_torque))
        print(f'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>instant_torque={instant_torque}')
        instant_speed = int(random.uniform(self.min_speed, self.max_speed))
        instant_thrust = int(random.uniform(self.min_thrust, self.max_thrust))
        instant_revolution = int(random.uniform(self.min_revolution, self.max_revolution))
        instant_power = FormulaCalculator.calculate_instant_power(instant_torque, instant_speed)
        if name == 'sps1':
            gdata.sps1_torque = instant_torque
            gdata.sps1_speed = instant_speed
            gdata.sps1_thrust = instant_thrust
            gdata.sps1_power = instant_power
            gdata.sps1_rounds = instant_revolution
        else:
            gdata.sps2_torque = instant_torque
            gdata.sps2_speed = instant_speed
            gdata.sps2_thrust = instant_thrust
            gdata.sps2_power = instant_power
            gdata.sps2_rounds = instant_revolution
