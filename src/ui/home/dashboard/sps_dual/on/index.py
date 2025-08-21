import asyncio
import logging
import flet as ft
from ui.home.dashboard.sps_dual.on.dual_instant_grid import DualInstantGrid
from ui.home.dashboard.eexi.eexi_limited_power import EEXILimitedPower
from ui.home.dashboard.chart.single_power_line import SinglePowerLine
from common.global_data import gdata


class DualShaPoLiOn(ft.Container):
    def __init__(self):
        super().__init__()
        self.task_running = True

    def build(self):
        try:
            if self.page is None or self.page.window is None:
                return

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
        except:
            logging.exception('exception occured at DualShaPoLiOn.build')

    async def load_data(self):
        while self.task_running:
            try:
                self.instant_grid.reload()
                self.eexi_limited_power.reload()
                self.power_chart.reload()
            except:
                logging.exception("exception occured at DualShaPoLiOn.load_data")
                break
            await asyncio.sleep(gdata.configPreference.data_collection_seconds_range)

    def did_mount(self):
        self.task_running = True
        if self.page:
            self.task = self.page.run_task(self.load_data)

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()
