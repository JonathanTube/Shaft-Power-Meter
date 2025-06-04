import asyncio
import random
import logging

from db.models.counter_log import CounterLog
from db.models.data_log import DataLog
from db.models.system_settings import SystemSettings
from common.global_data import gdata
from db.models.alarm_log import AlarmLog
from db.models.event_log import EventLog
from db.models.report_info import ReportInfo
from utils.data_saver import DataSaver


class TestModeTask:
    def __init__(self):
        self.min_torque = 0
        self.max_torque = 0
        self.min_speed = 0
        self.max_speed = 0
        self.min_thrust = 0
        self.max_thrust = 0
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

    async def generate_random_data(self):
        self.is_running = True

        system_settings: SystemSettings = SystemSettings.get()
        amount_of_propeller = system_settings.amount_of_propeller

        while self.is_running:
            await self.save_generated_data('sps1')
            if amount_of_propeller == 2:
                await self.save_generated_data('sps2')
            await asyncio.sleep(1)

    async def start(self):
        asyncio.create_task(self.generate_random_data())

    def stop(self):
        try:
            DataLog.truncate_table()
            AlarmLog.truncate_table()
            EventLog.truncate_table()
            ReportInfo.truncate_table()
            CounterLog.truncate_table()
            gdata.sps1_speed = 0
            gdata.sps1_power = 0
            gdata.sps1_torque = 0
            gdata.sps1_thrust = 0

            gdata.sps2_speed = 0
            gdata.sps2_power = 0
            gdata.sps2_torque = 0
            gdata.sps2_thrust = 0

            gdata.sps1_power_history = []
            gdata.sps2_power_history = []
        except Exception:
            logging.exception('test mode task error')
        self.is_running = False

    async def save_generated_data(self, name):
        instant_torque = int(random.uniform(self.min_torque, self.max_torque))
        instant_speed = int(random.uniform(self.min_speed, self.max_speed))
        instant_thrust = int(random.uniform(self.min_thrust, self.max_thrust))
        DataSaver.save(name, 0, 0, 0, instant_torque, 0, 0, instant_thrust, instant_speed)


testModeTask: TestModeTask = TestModeTask()
