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
            await self.generate_data()
            await asyncio.sleep(self.update_interval)

    def stop(self):
        self.is_running = False

    async def generate_data(self):
        """Generate random data and save to database"""
        try:
            # Generate random data
            data = DataLog.create(
                utc_date=datetime.now().date(),
                utc_time=datetime.now().time(),
                revolution=round(random.uniform(900, 1100), 2),  # Rev/Min
                power=round(random.uniform(900, 1100), 2),  # kW
                thrust=round(random.uniform(900, 1100), 2),  # kN
                torque=round(random.uniform(900, 1100), 2)  # kNm
            )
            print(f"Generated data: {data}")
        except Exception as e:
            print(f"Error generating data: {e}")


# async def main():
#     logger = DataLogger()
#     try:
#         await logger.start()
#     except KeyboardInterrupt:
#         logger.stop()
#         print("Data logger stopped")


# if __name__ == "__main__":
#     asyncio.run(main())
