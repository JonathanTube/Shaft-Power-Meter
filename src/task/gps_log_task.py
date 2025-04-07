import asyncio
import random

import flet as ft
from db.models.gps_log import GpsLog


class GpsLogTask:
    def __init__(self, page: ft.Page):
        self.page = page
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
        try:
            utc_date_time = self.__get_session('utc_date_time')
            longitude = round(random.uniform(-180, 180), 2)
            latitude = round(random.uniform(-90, 90), 2)
            location = f"{longitude},{latitude}"
            self.__set_session('instant_gps_location', location)
            GpsLog.create(location=location, utc_date_time=utc_date_time)
        except Exception as e:
            print(f"Error generating GPS data: {e}")
            self.__set_session('instant_gps_location', None)

    def __set_session(self, key: str, value: any):
        self.page.session.set(key, value)

    def __get_session(self, key: str):
        return self.page.session.get(key)
