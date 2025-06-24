import asyncio
import logging
import flet as ft
from db.models.preference import Preference
from ui.home.dashboard.sps_single.off.single_meters import SingleMeters
from ui.home.dashboard.thrust.index import ThrustBlock


class SingleShaPoLiOff(ft.Stack):
    def __init__(self):
        super().__init__()
        self.task_running = False

    def build(self):
        try:
            self.thrust_power = ThrustBlock("sps1")
            self.single_meters = SingleMeters()

            self.controls = [
                self.thrust_power,
                ft.Column(
                    expand=True,
                    spacing=10,
                    alignment=ft.alignment.center,
                    controls=[
                        self.single_meters
                    ]
                )
            ]
        except:
            logging.exception('exception occured at SingleShaPoLiOff.build')


    async def load_data(self):
        preference: Preference = Preference.get()
        interval = preference.data_refresh_interval
        while self.task_running:
            try:
                self.single_meters.reload()
                self.thrust_power.reload()
            except:
                logging.exception("exception occured at SingleShaPoLiOff.load_data")
                break
            finally:
                await asyncio.sleep(interval)

    def did_mount(self):
        self.task_running = True
        self.task = self.page.run_task(self.load_data)

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()
