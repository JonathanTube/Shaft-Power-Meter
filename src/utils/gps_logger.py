import asyncio
import random
from datetime import datetime

from db.models.gps_log import GpsLog


class GpsLogger:
    def __init__(self):
        self.is_running = False
        self.update_interval = 1.0  # seconds

    async def start(self):
        self.is_running = True
        while self.is_running:
            await self.generate_gps_data()
            await asyncio.sleep(self.update_interval)

    def stop(self):
        self.is_running = False

    async def generate_gps_data(self):
        """Generate random GPS data and save to database"""
        try:
            # Generate random GPS data
            gps_data = GpsLog.create(
                utc_date=datetime.now().date(),
                utc_time=datetime.now().time(),
                longitude=round(random.uniform(-180, 180), 2),
                latitude=round(random.uniform(-90, 90), 2)
            )
            # print(f"Generated GPS data: {gps_data}")
        except Exception as e:
            print(f"Error generating GPS data: {e}")
