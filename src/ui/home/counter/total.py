import asyncio
import logging
import flet as ft
from typing import Literal
from ui.home.counter.display import CounterDisplay
from common.global_data import gdata


class TotalCounter(ft.Container):
    def __init__(self, name: Literal['sps', 'sps2']):
        super().__init__()
        self.name = name

        self.height = 280
        self.expand = True
        self.border_radius = ft.border_radius.all(10)
        self.padding = 10
        self.border = ft.border.all(width=0.5, color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE))

        self.task = None
        self.task_running = False

    def build(self):
        try:
            if self.page and self.page.session:
                self.display = CounterDisplay()
                self.time_elapsed = ft.Text("")

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
                    spacing=20,
                    controls=[
                        ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[self.title, self.status_container]),
                        self.display,
                        ft.Column(
                            spacing=0,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                self.time_elapsed
                            ]
                        )
                    ])

                self.txt_measured = self.page.session.get("lang.counter.measured")
                self.txt_started_at = self.page.session.get("lang.counter.started_at")
        except:
            logging.exception('exception occured at TotalCounter.build')

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
                time_elapsed = 0
                if self.name == 'sps':
                    time_elapsed = gdata.configCounterSPS.Total.seconds
                else:
                    time_elapsed = gdata.configCounterSPS2.Total.seconds

                days = time_elapsed // (24 * 3600)
                hours = (time_elapsed % (24 * 3600)) // 3600
                minutes = (time_elapsed % 3600) // 60
                seconds = time_elapsed % 60

                time_elapsed = f'{days:02d} d {hours:02d}:{minutes:02d}:{seconds:02d} h'

                if self.time_elapsed and self.time_elapsed.page:
                    self.time_elapsed.value = f'{time_elapsed} {self.txt_measured}'
                    self.time_elapsed.visible = True
                    self.time_elapsed.update()

                if self.display:
                    system_unit = gdata.configPreference.system_unit

                    avg_power = 0
                    total_energy = 0
                    avg_speed = 0

                    if self.name == 'sps':
                        avg_power = gdata.configCounterSPS.Total.avg_power
                        total_energy = gdata.configCounterSPS.Total.total_energy
                        avg_speed = gdata.configCounterSPS.Total.avg_speed
                    else:
                        avg_power = gdata.configCounterSPS2.Total.avg_power
                        total_energy = gdata.configCounterSPS2.Total.total_energy
                        avg_speed = gdata.configCounterSPS2.Total.avg_speed

                    self.display.set_average_power(avg_power, system_unit)
                    self.display.set_total_energy(total_energy, system_unit)
                    self.display.set_average_speed(avg_speed)
            except:
                logging.exception('TotalCounter.loop')
            await asyncio.sleep(gdata.configPreference.data_collection_seconds_range)
