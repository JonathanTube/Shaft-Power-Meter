import asyncio
import flet as ft
from db.models.io_conf import IOConf
from db.models.system_settings import SystemSettings
from utils.plc_util import plc_util
from common.global_data import gdata


class SelfTest(ft.Tabs):
    def __init__(self):
        super().__init__()
        self.system_settings:SystemSettings = SystemSettings.get()
        self.conf: IOConf = IOConf.get()
        self.plc_task = None
        self.sps1_task = None
        self.sps2_task = None

        self.hmi_server_task = None

    def build(self):
        self.plc_log = ft.ListView(
            padding=10, auto_scroll=True, height=500, spacing=5, expand=True)
        
        self.sps1_log = ft.ListView(
            padding=10, auto_scroll=True, height=500, spacing=5, expand=True)
        
        self.sps2_log = ft.ListView(
            padding=10, auto_scroll=True, height=500, spacing=5, expand=True)
        
        self.gps_log = ft.ListView(
            padding=10, auto_scroll=True, height=500, spacing=5, expand=True)
        
        self.hmi_server_log = ft.ListView(
            padding=10, auto_scroll=True, height=500, spacing=5, expand=True)
        
        self.tabs = [
            ft.Tab(text="SPS-1", content=self.sps1_log, visible=self.conf.connect_to_sps),
            ft.Tab(text="SPS-2", content=self.sps2_log, visible=self.conf.connect_to_sps and self.system_settings.amount_of_propeller == 2),
            ft.Tab(text="HMI Server", content=self.hmi_server_log, visible=not self.conf.connect_to_sps),
            ft.Tab(text="GPS", content=self.gps_log),
            ft.Tab(text="PLC", content=self.plc_log, visible=self.conf.plc_enabled)
        ]

    def did_mount(self):
        if self.conf.plc_enabled:
            self.plc_task = self.page.run_task(self.__read_plc_data)

        if self.conf.connect_to_sps:
            self.sps1_task = self.page.run_task(self.__read_sps1_data)
            if gdata.amount_of_propeller == 2:
                self.sps2_task = self.page.run_task(self.__read_sps2_data)
        else:
            self.hmi_server_task = self.page.run_task(self.__read_hmi_server_data)

        # self.page.run_task(self.__read_gps_data)

    def will_unmount(self):
        if self.conf.plc_enabled and self.plc_task:
            self.plc_task.cancel()

        if self.conf.connect_to_sps:
            if self.sps1_task:
                self.sps1_task.cancel()

            if self.sps2_task and gdata.amount_of_propeller == 2:
                self.sps2_task.cancel()
        else:
            self.hmi_server_task.cancel()

    async def __read_plc_data(self):
        while True:
            try:
                plc_4_20_ma_data = await plc_util.read_4_20_ma_data()
                self.plc_log.controls.append(
                    ft.Text(f"4-20mA: {plc_4_20_ma_data}"))
                self.plc_log.controls.append(ft.Text(f"alarm: {await plc_util.read_alarm()}"))
                self.plc_log.controls.append(ft.Text(f"overload: {await plc_util.read_power_overload()}"))
                self.plc_log.controls.append(ft.Text(f"instant data: {await plc_util.read_instant_data()}"))
                self.plc_log.update()
            except Exception as e:
                self.plc_log.controls.append(ft.Text(f"error: {e}"))
                self.plc_log.update()
            await asyncio.sleep(2)

    async def __read_sps1_data(self):
        while True:
            sps1_data = f'ad0={gdata.sps1_ad0}, ad1={gdata.sps1_ad1}, speed={gdata.sps1_speed}'
            self.sps1_log.controls.append(ft.Text(f"SPS-1 Data: {sps1_data}"))
            self.sps1_log.update()
            await asyncio.sleep(1)

    async def __read_sps2_data(self):
        while True:
            sps2_data = f'ad0={gdata.sps2_ad0}, ad1={gdata.sps2_ad1}, speed={gdata.sps2_speed}'
            self.sps2_log.controls.append(ft.Text(f"SPS-2 Data: {sps2_data}"))
            self.sps2_log.update()
            await asyncio.sleep(1)

    async def __read_hmi_server_data(self):
        while True:
            sps1_data = f'sps1: torque={gdata.sps1_torque}, thrust={gdata.sps1_thrust}, speed={gdata.sps1_speed}'
            sps2_data = f'sps2: torque={gdata.sps2_torque}, thrust={gdata.sps2_thrust}, speed={gdata.sps2_speed}'
            self.hmi_server_log.controls.append(ft.Text(f"HMI Server Data: {sps1_data}"))
            self.hmi_server_log.controls.append(ft.Text(f"HMI Server Data: {sps2_data}"))
            self.hmi_server_log.update()
            await asyncio.sleep(1)
    # async def __read_gps_data(self):
    #     while True:
    #         gps_data = await gps_util.read_gps_data()
    #         self.gps_log.controls.append(ft.Text(f"GPS Data: {gps_data}"))
    #         self.gps_log.update()
    #         await asyncio.sleep(1)
