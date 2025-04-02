import asyncio
from typing import Literal
import flet as ft
from peewee import fn
from datetime import datetime, timedelta

from db.models.data_log import DataLog
from db.models.preference import Preference
from ui.common.simple_card import SimpleCard
from ui.common.toast import Toast
from .display import CounterDisplay


class CounterInterval(ft.Container):
    def __init__(self, name: Literal['SPS1', 'SPS2']):
        super().__init__()
        self.expand = True
        self.hours = 24
        self.name = name
        self.__load_config()

    def __load_config(self):
        self.system_unit = Preference.get().system_unit

    def on_hours_change(self, e):
        if not e.control.value:
            Toast.show_error(e.page, "Interval cannot be empty")
            return

        _hours = float(e.control.value)

        if _hours <= 0:
            Toast.show_error(e.page, "Interval must be greater than 0")
            return

        self.hours = _hours
        Toast.show_success(
            e.page, f"Interval has been set to {self.hours} hours")

    def build(self):
        self.display = CounterDisplay()

        self.hours_field = ft.TextField(
            label="Interval Setting",
            suffix_text="Hours",
            width=220,
            height=40,
            text_size=14,
            input_filter=ft.InputFilter(
                regex_string=r'^[0-9]+(\.[0-9]+)?$'
            ),
            value=self.hours,
            border_color=ft.colors.ON_SURFACE,
            size_constraints=ft.BoxConstraints(max_height=40),
            on_change=lambda e: self.on_hours_change(e)
        )

        self.content = SimpleCard(
            title="Interval",
            expand=False,
            body=ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    self.display,
                    self.hours_field
                ]))

    def did_mount(self):
        self._task = self.page.run_task(self.__refresh_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    async def __refresh_data(self):
        while True:
            data_log = DataLog.select(
                fn.COALESCE(fn.AVG(DataLog.power), 0).alias('average_power'),
                fn.COALESCE(fn.AVG(DataLog.speed), 0).alias('average_speed')
            ).where(
                DataLog.name == self.name,
                DataLog.created_at > datetime.now() - timedelta(hours=self.hours)
            ).dicts().get()
            average_power = data_log['average_power']
            sum_power = average_power * self.hours / 1000
            number_of_revolutions = 0
            average_speed = data_log['average_speed']
            self.display.set_average_power(average_power, self.system_unit)
            self.display.set_sum_power(sum_power, self.system_unit)
            self.display.set_number_of_revolutions(number_of_revolutions)
            self.display.set_average_speed(average_speed)
            await asyncio.sleep(1)
