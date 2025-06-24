import asyncio
from datetime import datetime, timedelta
import logging

from db.models.date_time_conf import DateTimeConf
from common.global_data import gdata


class UtcTimer:
    def __init__(self) -> None:
        self.task_running = True

    async def start(self):
        date_time_conf: DateTimeConf = DateTimeConf.get()
        gdata.utc_date_time = date_time_conf.utc_date_time

        while self.task_running:
            try:
                # add 1 second
                gdata.utc_date_time = gdata.utc_date_time + timedelta(seconds=1)
                gdata.system_date_time = datetime.now()

                DateTimeConf.update(
                    utc_date_time=gdata.utc_date_time,
                    system_date_time=gdata.system_date_time
                ).where(
                    DateTimeConf.id == date_time_conf.id
                ).execute()
            except:
                logging.exception('exception occured at UtcTimer.start')
            finally:
                await asyncio.sleep(1)
