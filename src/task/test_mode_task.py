import asyncio
import random

from db.models.data_log import DataLog
from utils.formula_cal import FormulaCalculator

class TestModeTask:
    def __init__(self, page):
        self.page = page
        self.min_torque = 0
        self.max_torque = 0
        self.min_speed = 0
        self.max_speed = 0
        self.min_thrust = 0
        self.max_thrust = 0
        self.min_revolution = 0
        self.max_revolution = 0
        self.time_interval = 0
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

    def set_time_interval(self, time_interval):
        self.time_interval = time_interval

    async def start(self):
        self.is_running = True
        # start a thread to generate random data every time_interval seconds
        return asyncio.create_task(self.generate_random_data())

    def stop(self):
        try:
            DataLog.truncate_table()
        except Exception as e:
            print(f'Error truncating DataLog table: {e}')
        self.is_running = False
    
        
    async def generate_random_data(self):
        print(f'self.is_running={self.is_running}')
        while self.is_running:
            # start to generate random data in range of min and max
            # print(f'generate_random_data')
            await self.save_generated_data('sps1')
            await self.save_generated_data('sps2')
            await asyncio.sleep(self.time_interval)

    async def save_generated_data(self,name):
        instant_torque = random.randint(self.min_torque, self.max_torque)
        instant_speed = random.randint(self.min_speed, self.max_speed)
        instant_thrust = random.randint(self.min_thrust, self.max_thrust)
        instant_revolution = random.randint(self.min_revolution, self.max_revolution)
        instant_power = FormulaCalculator.calculate_instant_power(instant_torque, instant_speed)
        utc_date_time = self.page.session.get('utc_date_time')
        
        DataLog.create(
            name=name,
            utc_date_time=utc_date_time,
            torque=instant_torque,
            speed=instant_speed,
            thrust=instant_thrust,
            rounds=instant_revolution,
            power=instant_power
        )
        self.page.session.set(f'{name}_instant_torque', instant_torque)
        self.page.session.set(f'{name}_instant_speed', instant_speed)
        self.page.session.set(f'{name}_instant_thrust', instant_thrust)
        self.page.session.set(f'{name}_instant_revolution', instant_revolution)
        self.page.session.set(f'{name}_instant_power', instant_power)
