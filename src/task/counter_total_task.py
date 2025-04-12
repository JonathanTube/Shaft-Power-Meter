from db.models.data_log import DataLog
from db.models.preference import Preference
from db.models.system_settings import SystemSettings
from datetime import datetime, timedelta
from peewee import fn
from typing import Literal
import flet as ft
import asyncio


class CounterTotalTask:
    def __init__(self, page: ft.Page):
        self.page = page

    async def start(self):
        preference: Preference = Preference.get()
        system_settings: SystemSettings = SystemSettings.get()
        while True:
            self.__calculate_all('sps1')
            if system_settings.amount_of_propeller == 2:
                self.__calculate_all('sps2')

            await asyncio.sleep(preference.data_refresh_interval)

    def __calculate_all(self, name: Literal['sps1', 'sps2']):
        data_log = DataLog.select(
            fn.COALESCE(fn.AVG(DataLog.power), 0).alias('average_power'),
            fn.COALESCE(fn.MIN(DataLog.rounds), 0).alias('min_rounds'),
            fn.COALESCE(fn.MAX(DataLog.rounds), 0).alias('max_rounds'),
            fn.COALESCE(fn.MIN(DataLog.created_at), 0).alias('start_time'),
            fn.COALESCE(fn.MAX(DataLog.created_at), 0).alias('end_time')
        ).where(
            DataLog.name == name
        ).dicts().get()

        str_format = '%Y-%m-%d %H:%M:%S.%f'
        start_time = datetime.strptime(data_log['start_time'], str_format)
        end_time = datetime.strptime(data_log['end_time'], str_format)
        average_power = data_log['average_power']
        max_rounds = data_log['max_rounds']
        min_rounds = data_log['min_rounds']

        self.__handle_result(name, start_time, end_time,
                             average_power, max_rounds, min_rounds)

    def __handle_result(self, name: Literal['sps1', 'sps2'], start_time: datetime, end_time: datetime, average_power: float, max_rounds: int, min_rounds: int):
        hours = (end_time - start_time).total_seconds() / 3600

        total_energy = (average_power * hours) / 1000  # kWh

        total_rounds = max_rounds - min_rounds

        average_speed = 0
        if hours > 0:
            average_speed = round(total_rounds / (hours * 60), 1)

        time_elapsed = end_time - start_time
        days = time_elapsed.days
        hours = time_elapsed.seconds // 3600
        minutes = (time_elapsed.seconds % 3600) // 60
        seconds = time_elapsed.seconds % 60

        self.page.session.set(f'counter_total_{name}', {
            'total_energy': total_energy,
            'average_power': average_power,
            'total_rounds': total_rounds,
            'average_speed': average_speed,
            'time_elapsed': f'{days:02d} d {hours:02d}:{minutes:02d}:{seconds:02d} h',
            'started_at': start_time.strftime("%Y-%m-%d %H:%M:%S")
        })
