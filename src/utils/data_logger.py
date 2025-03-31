import asyncio
import random
from datetime import datetime

from db.models.data_log import DataLog
from db.models.propeller_setting import PropellerSetting


class DataLogger:
    def __init__(self):
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
            await self.generate_data("SPS1")
            await self.generate_data("SPS2")
            await asyncio.sleep(self.update_interval)

    def stop(self):
        self.is_running = False

    async def generate_data(self, name):
        """Generate random data and save to database"""
        try:
            # Generate random data
            DataLog.create(
                name=name,
                utc_date=datetime.now().date(),
                utc_time=datetime.now().time(),
                # rpm
                revolution=random.randint(
                    int(self.max_speed * 0.7),
                    self.max_speed
                ),
                # W
                power=random.randint(
                    int(self.max_power * 0.7),
                    self.max_power
                ),
                thrust=random.randint(500, 1000),  # N
                torque=random.randint(500, 1000)  # Nm
            )
            # print(f"Generated data: {data}")
        except Exception as e:
            print(f"Error generating data: {e}")
