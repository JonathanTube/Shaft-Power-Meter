import asyncio
import logging
import flet as ft
from db.models.preference import Preference
from ui.home.dashboard.sps_dual.off.dual_meters import DualMeters
from ui.home.dashboard.chart.dual_power_line import DualPowerLine


class DualShaPoLiOff(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def build(self):
        self.sps1_meters = DualMeters(name="sps1")
        self.sps2_meters = DualMeters(name="sps2")
        self.dual_power_line = DualPowerLine()

        self.content = ft.Column(
            expand=True,
            spacing=10,
            controls=[
                ft.Row(
                    expand=True,
                    spacing=10,
                    controls=[self.sps1_meters, self.sps2_meters]
                )
            ]
        )

    async def load_data(self):
        preference: Preference = Preference.get()
        interval = preference.data_refresh_interval
        while True:
            try:
                self.sps1_meters.reload()
                self.sps2_meters.reload()
            except Exception as e:
                logging.exception(e)
            await asyncio.sleep(interval)

    def did_mount(self):
        self.task = self.page.run_task(self.load_data)

    def will_unmount(self):
        if self.task:
            self.task.cancel()
