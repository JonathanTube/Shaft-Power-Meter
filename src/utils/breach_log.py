import asyncio
from datetime import datetime
from db.models.event_log import EventLog


class BreachLogger:
    def __init__(self):
        self.is_running = False
        self.update_interval = 1.0  # seconds

    async def start(self):
        self.is_running = True
        while self.is_running:
            await self.generate_breach_data()
            await asyncio.sleep(self.update_interval)

    def stop(self):
        self.is_running = False

    async def generate_breach_data(self):
        """Generate random GPS data and save to database"""
        try:
            # Generate random Breach data
            breach_data = EventLog.create(
                breach_reason=1,
                started_at=datetime.now(),
                started_position="2021-01-01 00:00:00",
                ended_at=datetime.now(),
                ended_position="2021-01-01 00:00:00",
                note="test"
            )
            # print(f"Generated Breach data: {breach_data}")
        except Exception as e:
            print(f"Error generating Breach data: {e}")
