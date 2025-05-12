import asyncio
import flet as ft
from utils.plc_util import plc_util


class SelfTest(ft.Tabs):
    def __init__(self):
        super().__init__()
        self.plc_task = None

    def build(self):
        self.plc_log = ft.ListView(padding=10, auto_scroll=True, height=500, spacing=5, expand=True)
        self.sps_log = ft.ListView(padding=10, auto_scroll=True, height=500, spacing=5, expand=True)
        self.gps_log = ft.ListView(padding=10, auto_scroll=True, height=500, spacing=5, expand=True)
        self.tabs = [ft.Tab(text="PLC", content=self.plc_log), ft.Tab(text="SPS", content=self.sps_log), ft.Tab(text="GPS", content=self.gps_log)]

    def did_mount(self):
        self.plc_task = self.page.run_task(self.__read_plc_data)
        # self.page.run_task(self.__read_sps_data)
        # self.page.run_task(self.__read_gps_data)

    def will_unmount(self):
        if self.plc_task:
            self.plc_task.cancel()

    async def __read_plc_data(self):
        while True:
            try:
                plc_4_20_ma_data = await plc_util.read_4_20_ma_data()
                self.plc_log.controls.append(ft.Text(f"4-20mA: {plc_4_20_ma_data}"))
                self.plc_log.controls.append(ft.Text(f"alarm: {await plc_util.read_alarm()}"))
                self.plc_log.controls.append(ft.Text(f"overload: {await plc_util.read_power_overload()}"))
                self.plc_log.controls.append(ft.Text(f"instant data: {await plc_util.read_instant_data()}"))
                self.plc_log.update()
            except Exception as e:
                self.plc_log.controls.append(ft.Text(f"error: {e}"))
                self.plc_log.update()
            await asyncio.sleep(5)

    # async def __read_sps_data(self):
    #     while True:
    #         sps_data = await sps_util.read_sps_data()
    #         self.sps_log.controls.append(ft.Text(f"SPS Data: {sps_data}"))
    #         self.sps_log.update()
    #         await asyncio.sleep(1)

    # async def __read_gps_data(self):
    #     while True:
    #         gps_data = await gps_util.read_gps_data()
    #         self.gps_log.controls.append(ft.Text(f"GPS Data: {gps_data}"))
    #         self.gps_log.update()
    #         await asyncio.sleep(1)
