import asyncio
from datetime import datetime, timezone


class UtcTimer:
    def __init__(self):
        
        self.utc_time = None

    async def start(self):
        while True:
            # get utc time from local time of host machine
            self.utc_time = datetime.now(timezone.utc)
            print(self.utc_time)
            await asyncio.sleep(1)

    def get_utc_time(self):
        return self.utc_time
