import flet as ft
import asyncio
import logging
from datetime import timedelta
from peewee import fn
from typing import Literal
from db.models.data_log import DataLog
from ui.common.toast import Toast
from .display import CounterDisplay
from ui.common.keyboard import keyboard
from common.global_data import ConfigCounterSPS, ConfigCounterSPS2, gdata


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

                self.init_data()
                Toast.show_success(e.page, self.page.session.get('lang.counter.interval_has_been_changed'))
        except:
            logging.exception('exception occured at AlarmList.on_hours_change')

    def did_mount(self):
        self.task_running = True
        if self.page:
            self.task = self.page.run_task(self.loop)

        # 不为空直接跳过
        if self.name == 'sps' and gdata.configCounterSPS.Interval.start_at:
            return
        # 不为空直接跳过
        if self.name == 'sps2' and gdata.configCounterSPS2.Interval.start_at:
            return
        self.init_data()

    def init_data(self):
        threshold = gdata.configDateTime.utc - timedelta(hours=self.hours)
        if self.name == 'sps':
            result = DataLog.select(
                fn.MIN(DataLog.utc_date_time).alias("start_at"),
                fn.COUNT(DataLog.id).alias("times"),
                fn.SUM(DataLog.power).alias("sum_power"),
                fn.SUM(DataLog.speed).alias("sum_speed")
            ).where(DataLog.utc_date_time >= threshold, DataLog.name == 'sps').dicts().get()

            start_at = result['start_at']
            times = result['times']
            sum_power = result["sum_power"]
            sum_speed = result["sum_speed"]

            ConfigCounterSPS.Interval.start_at = start_at or gdata.configDateTime.utc
            ConfigCounterSPS.Interval.times = times or 0
            ConfigCounterSPS.Interval.sum_power = sum_power or 0
            ConfigCounterSPS.Interval.sum_speed = sum_speed or 0.0
        else:
            result = DataLog.select(
                fn.MIN(DataLog.utc_date_time).alias("start_at"),
                fn.SUM(DataLog.power).alias("times"),
                fn.SUM(DataLog.power).alias("sum_power"),
                fn.SUM(DataLog.speed).alias("sum_speed")
            ).where(DataLog.utc_date_time >= threshold, DataLog.name == 'sps').dicts().get()

            start_at = result['start_at']
            times = result['times']
            sum_power = result["sum_power"]
            sum_speed = result["sum_speed"]

            ConfigCounterSPS2.Interval.start_at = start_at or gdata.configDateTime.utc
            ConfigCounterSPS2.Interval.times = times or 0
            ConfigCounterSPS2.Interval.sum_power = sum_power or 0
            ConfigCounterSPS2.Interval.sum_speed = sum_speed or 0.0

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()

    async def loop(self):
        while self.task_running:
            try:
                if self.display:
                    system_unit = gdata.configPreference.system_unit

                    avg_power = gdata.configCounterSPS.Interval.avg_power if self.name == 'sps' else gdata.configCounterSPS2.Interval.avg_power
                    self.display.set_average_power(avg_power, system_unit)

                    total_energy = gdata.configCounterSPS.Interval.total_energy if self.name == 'sps' else gdata.configCounterSPS2.Interval.total_energy
                    self.display.set_total_energy(total_energy, system_unit)

                    avg_speed = gdata.configCounterSPS.Interval.avg_speed if self.name == 'sps' else gdata.configCounterSPS2.Interval.avg_speed
                    self.display.set_average_speed(avg_speed)
            except:
                logging.exception("IntervalCounter.loop")
            finally:
                await asyncio.sleep(1)
