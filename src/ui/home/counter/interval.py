import asyncio
import logging
from datetime import datetime, timedelta
from typing import Literal
import flet as ft
from db.models.data_log import DataLog
from db.models.preference import Preference
from db.models.date_time_conf import DateTimeConf
from ui.common.toast import Toast
from .display import CounterDisplay
from ui.common.keyboard import keyboard
from peewee import fn
from common.global_data import gdata

class IntervalCounter(ft.Container):
    def __init__(self, name: Literal['sps1', 'sps2']):
        super().__init__()
        self.name = name

        self.expand = True
        self.border_radius = ft.border_radius.all(10)
        self.padding = 10
        self.border = ft.border.all(width=0.5, color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE))

        self.hours = 24
        preference: Preference = Preference.get()
        datetime_conf: DateTimeConf = DateTimeConf.get()
        self.system_unit = preference.system_unit
        self.interval = preference.data_refresh_interval
        self.date_format = datetime_conf.date_format

    def build(self):
        self.display = CounterDisplay()

        self.hours_field = ft.TextField(
            label=self.page.session.get('lang.counter.interval_setting'),
            suffix_text=self.page.session.get('lang.counter.hours'),
            width=220,
            height=40,
            text_size=14,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control),
            value=self.hours,
            border_color=ft.Colors.ON_SURFACE,
            size_constraints=ft.BoxConstraints(max_height=40),
            on_change=lambda e: self.on_hours_change(e)
        )

        self.status_container = ft.Container(
            content=ft.Text(value=self.page.session.get('lang.counter.running'), size=12),
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.GREEN_500,
            border_radius=ft.border_radius.all(40),
            padding=ft.padding.only(top=0, bottom=4, left=10, right=10)
        )

        self.title = ft.Text(
            self.page.session.get('lang.counter.interval'),
            weight=ft.FontWeight.BOLD,
            size=16
        )

        self.content = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[self.title, self.status_container]),
                self.display,
                self.hours_field
            ])

    def on_hours_change(self, e):
        if not e.control.value:
            Toast.show_error(e.page, self.page.session.get('lang.counter.interval_cannot_be_empty'))
            return

        h = float(e.control.value)

        if h <= 0:
            Toast.show_error(e.page, self.page.session.get('lang.counter.interval_must_be_greater_than_0'))
            return

        self.hours = h
        Toast.show_success(e.page, self.page.session.get('lang.counter.interval_has_been_changed'))

    def did_mount(self):
        self.task = self.page.run_task(self.__running)

    def will_unmount(self):
        if self.task:
            self.task.cancel()

    async def __running(self):
        while True:
            self.__calculate()
            await asyncio.sleep(self.interval)

    def __calculate(self):
        param_end_time = gdata.utc_date_time
        param_start_time = param_end_time - timedelta(hours=self.hours)

        logging.info(f'IntervalCounter param_start_time: {param_start_time}')
        logging.info(f'IntervalCounter param_end_time: {param_end_time}')

        data_log = DataLog.select(
            fn.COALESCE(fn.AVG(DataLog.power), 0).alias('average_power'),
            fn.COALESCE(fn.MIN(DataLog.rounds), 0).alias('min_rounds'),
            fn.COALESCE(fn.MAX(DataLog.rounds), 0).alias('max_rounds'),
            fn.COALESCE(fn.MIN(DataLog.utc_date_time), None).alias('start_time'),
            fn.COALESCE(fn.MAX(DataLog.utc_date_time), None).alias('end_time')
        ).where(
            DataLog.name == self.name,
            DataLog.utc_date_time >= param_start_time,
            DataLog.utc_date_time <= param_end_time
        ).dicts().get()

        average_power = data_log['average_power']
        max_rounds = data_log['max_rounds']
        min_rounds = data_log['min_rounds']

        if data_log['start_time'] is None or data_log['end_time'] is None:
            return

        start_time = datetime.strptime(data_log['start_time'], self.date_format)
        end_time = datetime.strptime(data_log['end_time'], self.date_format)

        hours = (end_time - start_time).total_seconds() / 3600

        total_energy = (average_power * hours) / 1000  # kWh

        total_rounds = max_rounds - min_rounds

        average_speed = 0
        if hours > 0:
            average_speed = round(total_rounds / (hours * 60), 1)

        self.display.set_average_power(average_power, self.system_unit)
        self.display.set_total_energy(total_energy, self.system_unit)
        self.display.set_total_rounds(total_rounds)
        self.display.set_average_speed(average_speed)
