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

                self.content = ft.Column(
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
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
            self.task = self.page.run_task(self.loop)

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()

    async def loop(self):
        while self.task_running:
            try:
                if self.display:
                    system_unit = gdata.configPreference.system_unit

                threshold = gdata.configDateTime.utc - timedelta(hours=self.hours) + timedelta(seconds=1)

                result = DataLog.select(
                    fn.MIN(DataLog.utc_date_time).alias("start_at"),
                    fn.COUNT(DataLog.id).alias("times"),
                    fn.SUM(DataLog.power).alias("sum_power"),
                    fn.SUM(DataLog.speed).alias("sum_speed")
                ).where(DataLog.utc_date_time >= threshold, DataLog.name == self.name).dicts().get()

                times = result['times']

                if times > 0:
                    sum_power = result["sum_power"]
                    sum_speed = result["sum_speed"]

                    # 平均功率
                    avg_power = round(sum_power / times)
                    self.display.set_average_power(avg_power, system_unit)

                    # 总能耗
                    start_at = result["start_at"]

                    time_elapsed = gdata.configDateTime.utc - start_at
                    # print('===============================interval')
                    # print(time_elapsed.total_seconds())

                    hours = time_elapsed.total_seconds() / 3600

                    total_energy = round(avg_power * hours / 1000)
                    self.display.set_total_energy(total_energy, system_unit)

                    # 平均转速
                    avg_speed = round(sum_speed / times)
                    self.display.set_average_speed(avg_speed)
            except:
                logging.exception("IntervalCounter.loop")
            finally:
                await asyncio.sleep(gdata.configPreference.data_collection_seconds_range)
