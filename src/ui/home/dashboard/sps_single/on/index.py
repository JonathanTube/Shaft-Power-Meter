import asyncio
import logging
import flet as ft
from common.global_data import gdata
from ui.home.dashboard.chart.single_power_line import SinglePowerLine
from ui.home.dashboard.eexi.eexi_limited_power import EEXILimitedPower
from ui.home.dashboard.sps_single.on.single_instant_grid import SingleInstantGrid


class SingleShaPoLiOn(ft.Container):
    def __init__(self):
        super().__init__()
        self.task = None
        self.task_running = False

    def build(self):
        try:
            w = self.page.window.width * 0.5
            h = self.page.window.height * 0.5

            self.eexi_limited_power = EEXILimitedPower(w, h)
            self.instant_value_grid = SingleInstantGrid(w, h)
            self.power_line_chart = SinglePowerLine()

            self.content = ft.Column(
                controls=[
                    ft.Row(
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[self.eexi_limited_power, self.instant_value_grid]
                    ),
                    self.power_line_chart
                ],
                expand=True
            )
        except:
            logging.exception("exception occured at SingleShaPoLiOn.build")

    async def load_data(self):
        while self.task_running:
            try:
                self.eexi_limited_power.reload()
                self.instant_value_grid.reload()
                self.power_line_chart.reload()
            except:
                logging.exception("exception occured at SingleShaPoLiOn.load_data")
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
