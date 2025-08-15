import asyncio
from datetime import datetime, timedelta
import logging
from typing import Literal
import flet as ft
from db.models.data_log import DataLog
from ui.common.toast import Toast
from .display import CounterDisplay
from ui.common.keyboard import keyboard
from common.global_data import gdata
from peewee import fn


class IntervalCounter(ft.Container):
    def __init__(self, name: Literal['sps', 'sps2']):
        super().__init__()
        self.name = name

        self.height = 280

        self.expand = True
        self.border_radius = ft.border_radius.all(10)
        self.padding = 10
        self.border = ft.border.all(width=0.5, color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE))

        self.hours = 24

        self.task = None
        self.task_running = False

    def build(self):
        try:
            if self.page and self.page.session:
                self.display = CounterDisplay()

                self.hours_field = ft.TextField(
                    label=self.page.session.get('lang.counter.interval_setting'),
                    suffix_text=self.page.session.get('lang.counter.hours'),
                    width=220,
                    height=40,
                    text_size=14,
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control),
                    value=self.hours,
                    border_color=ft.Colors.ON_SURFACE,
                    size_constraints=ft.BoxConstraints(max_height=40)
                )

                self.hours_confirm = ft.FilledButton(
                    text=self.page.session.get('lang.button.confirm'),
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: self.on_hours_change(e)
                )

                self.status_container = ft.Container(
                    content=ft.Text(value=self.page.session.get('lang.counter.running'), color=ft.Colors.WHITE, size=12),
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

                spacing = 20
                if self.page.window and self.page.window.height <= 600:
                    spacing = 5

                self.content = ft.Column(
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=spacing,
                    controls=[
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[self.title, self.status_container]),
                        self.display,
                        ft.Column(
                            alignment=ft.MainAxisAlignment.END,
                            expand=True,
                            controls=[
                                ft.Row(
                                    alignment=ft.alignment.center,
                                    controls=[
                                        self.hours_field,
                                        self.hours_confirm
                                    ]
                                )
                            ]
                        )
                    ])
        except:
            logging.exception('exception occured at IntervalCounter.build')

    def on_hours_change(self, e):
        try:
            if self.page and self.page.session:
                hours = self.hours_field.value
                if not hours:
                    Toast.show_error(e.page, self.page.session.get('lang.counter.interval_cannot_be_empty'))
                    return

                h = float(hours)

                if h <= 0:
                    Toast.show_error(e.page, self.page.session.get('lang.counter.interval_must_be_greater_than_0'))
                    return

                self.hours = h
                Toast.show_success(e.page, self.page.session.get('lang.counter.interval_has_been_changed'))
        except:
            logging.exception('exception occured at AlarmList.on_hours_change')

    def did_mount(self):
        self.task_running = True
        if self.page:
            self.task = self.page.run_task(self.__running)

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()

    async def __running(self):
        while self.task_running:
            try:
                self.__calculate()
            except:
                logging.exception("exception occured at IntervalCounter.__running")

            await asyncio.sleep(gdata.configPreference.data_refresh_interval)

    def __calculate(self):
        try:
            param_end_time = gdata.configDateTime.utc
            param_start_time = param_end_time - timedelta(hours=self.hours)

            data_log = DataLog.select(
                fn.COALESCE(fn.AVG(DataLog.power), 0).alias('average_power'),
                fn.COALESCE(fn.AVG(DataLog.speed), 0).alias('average_speed'),
                fn.COALESCE(fn.MIN(DataLog.utc_date_time), None).alias('start_time'),
                fn.COALESCE(fn.MAX(DataLog.utc_date_time), None).alias('end_time')
            ).where(
                DataLog.name == self.name,
                DataLog.utc_date_time >= param_start_time,
                DataLog.utc_date_time <= param_end_time
            ).dicts().get()

            average_power = data_log['average_power']
            average_speed = data_log['average_speed']

            if data_log['start_time'] is None or data_log['end_time'] is None:
                return

            date_time_format = '%Y-%m-%d %H:%M:%S'
            start_time = datetime.strptime(data_log['start_time'], date_time_format)
            end_time = datetime.strptime(data_log['end_time'], date_time_format)

            hours = (end_time - start_time).total_seconds() / 3600

            total_energy = (average_power * hours) / 1000  # kWh

            if self.display is not None:
                system_unit = gdata.configPreference.system_unit
                self.display.set_average_power(average_power, system_unit)
                self.display.set_total_energy(total_energy, system_unit)
                self.display.set_average_speed(average_speed)
        except:
            logging.exception("exception occured at IntervalCounter.__calculate")
