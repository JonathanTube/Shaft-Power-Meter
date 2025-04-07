import asyncio
import flet as ft
from datetime import datetime, timezone, timedelta

from db.models.date_time_conf import DateTimeConf


class UtcTimer:
    def __init__(self, page: ft.Page):
        self.page = page
        self.date_time_conf = DateTimeConf.get()
        utc_date = self.date_time_conf.utc_date
        utc_time = self.date_time_conf.utc_time

        # 如果utc_date和utc_time为空，则使用当前日期和时间
        if utc_date is None or utc_time is None:
            utc_date = datetime.now(timezone.utc).date()
            utc_time = datetime.now(timezone.utc).time()

        self.__set_utc_date_time(datetime.combine(utc_date, utc_time))

    async def start(self):
        while True:
            utc_date_time = self.__get_utc_date_time()
            utc_date_time += timedelta(seconds=1)
            self.date_time_conf.utc_date = utc_date_time.date()
            self.date_time_conf.utc_time = utc_date_time.time()
            self.date_time_conf.save()
            print('utc_date_time=', utc_date_time)
            # 更新时间
            self.__set_utc_date_time(utc_date_time)
            await asyncio.sleep(1)

    def __set_utc_date_time(self, utc_date_time: datetime):
        self.page.session.set("utc_date_time", utc_date_time)

    def __get_utc_date_time(self):
        return self.page.session.get("utc_date_time")
