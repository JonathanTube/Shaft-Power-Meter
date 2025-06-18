import asyncio
import logging
import flet as ft
from typing import Literal
from db.models.counter_log import CounterLog
from db.models.preference import Preference
from db.models.date_time_conf import DateTimeConf
from ui.home.counter.display import CounterDisplay
from common.global_data import gdata


class TotalCounter(ft.Container):
    def __init__(self, name: Literal['sps1', 'sps2']):
        super().__init__()
        self.name = name

        self.height = 280
        
        self.expand = True
        self.border_radius = ft.border_radius.all(10)
        self.padding = 10
        self.border = ft.border.all(width=0.5, color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE))

        preference: Preference = Preference.get()
        datetime_conf: DateTimeConf = DateTimeConf.get()
        self.system_unit = preference.system_unit
        self.interval = preference.data_refresh_interval
        self.standard_date_time_format = '%Y-%m-%d %H:%M:%S'
        self.date_format = datetime_conf.date_format

    def build(self):
        self.display = CounterDisplay()
        self.time_elapsed = ft.Text("")
        self.started_at = ft.Text("")

        self.title = ft.Text(self.page.session.get('lang.counter.total'), weight=ft.FontWeight.BOLD, size=16)

        self.status_container = ft.Container(
            content=ft.Text(value=self.page.session.get('lang.counter.running'), color=ft.Colors.WHITE, size=12),
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.GREEN_500,
            border_radius=ft.border_radius.all(40),
            padding=ft.padding.only(top=0, bottom=4, left=10, right=10)
        )

        self.content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5 if self.page.window.height <= 600 else 20,
            controls=[
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[self.title, self.status_container]),
                self.display,
                ft.Column(
                    spacing=0,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self.time_elapsed,
                        self.started_at
                    ]
                )
            ])

        self.txt_measured = self.page.session.get("lang.counter.measured")
        self.txt_started_at = self.page.session.get("lang.counter.started_at")

    def did_mount(self):
        self.task = self.page.run_task(self.__running)

    def will_unmount(self):
        if self.task:
            self.task.cancel()

    async def __running(self):
        while True:
            try:
                self.__calculate()
            except Exception as e:
                logging.exception(e)
            await asyncio.sleep(self.interval)

    def __calculate(self):
        counter_log = CounterLog.get_or_none(CounterLog.sps_name == self.name, CounterLog.counter_type == 2)
        if counter_log is None:
            return
        start_time = counter_log.start_utc_date_time
        end_time = gdata.utc_date_time

        average_power = counter_log.total_power / counter_log.times
        average_speed = counter_log.total_speed / counter_log.times

        hours = (end_time - start_time).total_seconds() / 3600

        total_energy = (average_power * hours) / 1000  # kWh

        time_elapsed = end_time - start_time
        days = time_elapsed.days
        hours = time_elapsed.seconds // 3600
        minutes = (time_elapsed.seconds % 3600) // 60
        seconds = time_elapsed.seconds % 60

        time_elapsed = f'{days:02d} d {hours:02d}:{minutes:02d}:{seconds:02d} h'
        started_at = start_time.strftime(f"{self.date_format} %H:%M:%S")

        self.time_elapsed.value = f'{time_elapsed} {self.txt_measured}'
        self.time_elapsed.visible = True
        self.time_elapsed.update()

        self.started_at.value = f'{self.txt_started_at} {started_at}'
        self.started_at.visible = True
        self.started_at.update()

        self.display.set_average_power(average_power, self.system_unit)
        self.display.set_total_energy(total_energy, self.system_unit)
        self.display.set_average_speed(average_speed)
