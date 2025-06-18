import asyncio
import logging
import flet as ft

from db.models.preference import Preference
from ui.home.dashboard.sps_dual.on.dual_instant_grid import DualInstantGrid
from ui.home.dashboard.eexi.eexi_limited_power import EEXILimitedPower
from ui.home.dashboard.chart.single_power_line import SinglePowerLine


class DualShaPoLiOn(ft.Container):
    def __init__(self):
        super().__init__()

    def build(self):
        w = self.page.window.width * 0.5
        h = self.page.window.height * 0.5

        self.eexi_limited_power = EEXILimitedPower(w, h)
        self.instant_grid = DualInstantGrid()
        self.power_chart = SinglePowerLine()

        self.content = ft.Column(
            expand=True,
            controls=[
                ft.Row(expand=True, controls=[self.eexi_limited_power, self.instant_grid]),
                ft.Row(expand=True, controls=[self.power_chart])
            ]
        )

    async def load_data(self):
        preference: Preference = Preference.get()
        interval = preference.data_refresh_interval
        while True:
            try:
                self.instant_grid.reload()
                self.eexi_limited_power.reload()
                self.power_chart.reload()
            except Exception as e:
                logging.exception(e)
            await asyncio.sleep(interval)

    def did_mount(self):
        self.task = self.page.run_task(self.load_data)

    def will_unmount(self):
        if self.task:
            self.task.cancel()
