import asyncio
from datetime import datetime
from typing import Literal
import flet as ft
from peewee import fn

from db.models.preference import Preference
from ui.common.simple_card import SimpleCard
from .display import CounterDisplay
from db.models.data_log import DataLog


class CounterTotal(ft.Container):
    def __init__(self, name: Literal['SPS1', 'SPS2']):
        super().__init__()
        self.expand = True
        self.name = name
        self.system_unit = Preference.get().system_unit

    def build(self):
        self.display = CounterDisplay()
        time_elapsed = ft.Text("00 d 23:10:01 h measured")
        started_at = ft.Text("started at 18/07/2014 06:56:19")

        self.content = SimpleCard(
            title="Total",
            expand=False,
            body=ft.Column(
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.display,
                    time_elapsed,
                    started_at
                ]))

    def did_mount(self):
        self._task = self.page.run_task(self.__refresh_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    async def __refresh_data(self):
        while True:
            data_log = DataLog.select(
                fn.MIN(DataLog.created_at).alias('start_time'),
                fn.MAX(DataLog.created_at).alias('end_time'),
                fn.COALESCE(fn.AVG(DataLog.power), 0).alias('average_power'),
                fn.COALESCE(fn.AVG(DataLog.speed), 0).alias('average_speed')
            ).where(DataLog.name == self.name).dicts().get()

            average_power = data_log['average_power']
            start_time = data_log['start_time']
            end_time = data_log['end_time']
            hours = (end_time - start_time).total_seconds() / 3600
            sum_power = average_power * hours / 1000

            average_speed = data_log['average_speed']
            number_of_revolutions = 0

            self.display.set_sum_power(sum_power, self.system_unit)
            self.display.set_average_power(average_power, self.system_unit)
            self.display.set_average_speed(average_speed)
            self.display.set_number_of_revolutions(number_of_revolutions)
            await asyncio.sleep(1)
