import asyncio
from datetime import datetime, timedelta

from db.models.date_time_conf import DateTimeConf


class UtcTimer:
    async def start(self):
        self.date_time_conf: DateTimeConf = DateTimeConf.get()
        self.utc_date_time: datetime = self.date_time_conf.utc_date_time

        while True:
            # add 1 second
            self.utc_date_time = self.utc_date_time + timedelta(seconds=1)
            # print(f"current utc_date_time: {self.utc_date_time}")
            self.date_time_conf.utc_date_time = self.utc_date_time
            self.date_time_conf.system_date_time = datetime.now()
            self.date_time_conf.save()
            await asyncio.sleep(1)

    def get_utc_date_time(self):
        return self.utc_date_time
    
    def set_utc_date_time(self, utc_date_time: datetime):
        self.utc_date_time = utc_date_time


utc_timer: UtcTimer = UtcTimer()
