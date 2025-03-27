import asyncio
import random
from datetime import datetime

from db.models.data_log import DataLog


class DataLogger:
    def __init__(self):
        self.is_running = False
        self.update_interval = 1.0  # seconds

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
                revolution=random.randint(100, 500),  # rpm
                power=random.randint(500, 1000),  # W
                thrust=random.randint(500, 1000),  # N
                torque=random.randint(500, 1000)  # Nm
            )
            # print(f"Generated data: {data}")
        except Exception as e:
            print(f"Error generating data: {e}")
