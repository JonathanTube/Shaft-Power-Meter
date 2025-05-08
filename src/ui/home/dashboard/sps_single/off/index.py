import asyncio
import flet as ft
from db.models.preference import Preference
from ui.home.dashboard.sps_single.off.single_meters import SingleMeters
from ui.home.dashboard.chart.single_power_line import SinglePowerLine
from ui.home.dashboard.thrust.thrust_power import ThrustPower


class SingleShaPoLiOff(ft.Stack):
    def __init__(self):
        super().__init__()

    def build(self):
        self.thrust_power = ThrustPower()
        self.single_meters = SingleMeters()
        self.power_line_chart = SinglePowerLine()

        self.controls = [
            self.thrust_power,
            ft.Column(
                expand=True,
                spacing=10,
                alignment=ft.alignment.center,
                controls=[
                    self.single_meters,
                    self.power_line_chart
                ]
            )
        ]

    async def load_data(self):
        preference: Preference = Preference.get()
        interval = preference.data_refresh_interval
        while True:
            self.single_meters.reload()
            self.thrust_power.reload()
            self.power_line_chart.reload()
            await asyncio.sleep(interval)

    def did_mount(self):
        self.task = self.page.run_task(self.load_data)

    def will_unmount(self):
        if self.task:
            self.task.cancel()
