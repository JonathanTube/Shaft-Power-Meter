from db.models.data_log import DataLog
from datetime import datetime, timedelta
from peewee import fn
from typing import Literal
import flet as ft
import asyncio

from db.models.preference import Preference
from db.models.system_settings import SystemSettings


class CounterIntervalTask:
    def __init__(self, page: ft.Page):
        self.page = page

    async def start(self):
        preference: Preference = Preference.get()
        system_settings: SystemSettings = SystemSettings.get()
        while True:
            hours = self.page.session.get('counter_interval_hours')
            # print(f'hours: {hours}')
            if hours is not None:
                start_time = datetime.now() - timedelta(hours=hours)
                end_time = datetime.now()

                self.__calculate_by_range('SPS1', start_time, end_time)
                # print(system_settings.amount_of_propeller)
                if system_settings.amount_of_propeller == 2:
                    self.__calculate_by_range('SPS2', start_time, end_time)

            await asyncio.sleep(preference.data_refresh_interval)

    def __calculate_by_range(self, name: Literal['SPS1', 'SPS2'], start_time: datetime, end_time: datetime):
        data_log = DataLog.select(
            fn.COALESCE(fn.AVG(DataLog.power), 0).alias('average_power'),
            fn.COALESCE(fn.MIN(DataLog.rounds), 0).alias('min_rounds'),
            fn.COALESCE(fn.MAX(DataLog.rounds), 0).alias('max_rounds'),
            fn.COALESCE(fn.MIN(DataLog.created_at), 0).alias('start_time'),
            fn.COALESCE(fn.MAX(DataLog.created_at), 0).alias('end_time')
        ).where(
            DataLog.name == name,
            DataLog.created_at >= start_time,
            DataLog.created_at <= end_time
        ).dicts().get()

        average_power = data_log['average_power']
        max_rounds = data_log['max_rounds']
        min_rounds = data_log['min_rounds']

        format_str = '%Y-%m-%d %H:%M:%S.%f'
        actual_start_time = datetime.strptime(data_log['start_time'], format_str)
        actual_end_time = datetime.strptime(data_log['end_time'], format_str)

        self.__handle_result(
            name,
            actual_start_time,
            actual_end_time,
            average_power,
            max_rounds,
            min_rounds
        )

    def __handle_result(self, name: Literal['SPS1', 'SPS2'], start_time: datetime, end_time: datetime, average_power: float, max_rounds: int, min_rounds: int):
        hours = (end_time - start_time).total_seconds() / 3600

        total_energy = (average_power * hours) / 1000  # kWh

        total_rounds = max_rounds - min_rounds

        average_speed = 0
        if hours > 0:
            average_speed = round(total_rounds / (hours * 60), 1)

        self.page.session.set(f'counter_interval_{name}', {
            'total_energy': total_energy,
            'average_power': average_power,
            'total_rounds': total_rounds,
            'average_speed': average_speed
        })
