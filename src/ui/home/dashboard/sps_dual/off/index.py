import asyncio
import logging
import flet as ft
from ui.home.dashboard.sps_dual.off.dual_meters import DualMeters
from common.global_data import gdata


class DualShaPoLiOff(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.task_running = False

    def build(self):
        try:
            self.sps_meters = DualMeters(name="sps")
            self.sps2_meters = DualMeters(name="sps2")

            self.content = ft.Column(
                expand=True,
                spacing=10,
                controls=[
                    ft.Row(
                        expand=True,
                        spacing=10,
                        controls=[self.sps_meters, self.sps2_meters]
                    )
                ]
            )
        except:
            logging.exception('exception occured at DualShaPoLiOff.build')

    async def load_data(self):
        while self.task_running:
            try:
                self.sps_meters.reload()
                self.sps2_meters.reload()
            except:
                logging.exception('exception occured at DualShaPoLiOff.load_data')
                break
            await asyncio.sleep(gdata.configPreference.data_refresh_interval)

    def did_mount(self):
        self.task_running = True
        if self.page:
            self.task = self.page.run_task(self.load_data)

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()
