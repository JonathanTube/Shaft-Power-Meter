import asyncio
import logging
import flet as ft
from task.plc_sync_task import plc
from task.gps_sync_task import gps
from websocket.websocket_slave import ws_client
from common.global_data import gdata
from task.sps_read_task import sps_read_task
from task.sps2_read_task import sps2_read_task


class SelfTest(ft.Tabs):
    def __init__(self):
        super().__init__()
        self.plc_task = None
        self.sps_task = None
        self.sps2_task = None
        self.hmi_server_task = None
        self.gps_task = None

        self.task_running = False

    def build(self):
        try:
            if self.page and self.page.session:
                self.plc_log = ft.ListView(
                    padding=10, auto_scroll=True, height=500, spacing=5, expand=True)

                self.sps_log = ft.ListView(
                    padding=10, auto_scroll=True, height=500, spacing=5, expand=True)

                self.sps2_log = ft.ListView(
                    padding=10, auto_scroll=True, height=500, spacing=5, expand=True)

                self.gps_log = ft.ListView(
                    padding=10, auto_scroll=True, height=500, spacing=5, expand=True)

                self.hmi_server_log = ft.ListView(
                    padding=10, auto_scroll=True, height=500, spacing=5, expand=True)

                self.tabs = [
                    ft.Tab(text="SPS", content=self.sps_log, visible=gdata.configCommon.is_master),
                    ft.Tab(text="SPS2", content=self.sps2_log, visible=gdata.configCommon.is_master and gdata.configCommon.amount_of_propeller == 2),
                    ft.Tab(text="HMI Server", content=self.hmi_server_log, visible=not gdata.configCommon.is_master),
                    ft.Tab(text="GPS", content=self.gps_log, visible=gdata.configCommon.enable_gps),
                    ft.Tab(text="PLC", content=self.plc_log, visible=gdata.configCommon.enable_plc)
                ]
        except:
            logging.exception('exception occured at SelfTest.build')

    def did_mount(self):
        self.task_running = True

        if gdata.configCommon.enable_plc:
            self.plc_task = self.page.run_task(self.__read_plc_data)

        if gdata.configCommon.is_master:
            self.sps_task = self.page.run_task(self.__read_sps_data)
            if gdata.configCommon.amount_of_propeller == 2:
                self.sps2_task = self.page.run_task(self.__read_sps2_data)
        else:
            self.hmi_server_task = self.page.run_task(self.__read_hmi_server_data)

        if gdata.configCommon.enable_gps:
            self.gps_task = self.page.run_task(self.__read_gps_data)

    def will_unmount(self):
        self.task_running = False

        if gdata.configCommon.enable_plc and self.plc_task:
            self.plc_task.cancel()

        if gdata.configCommon.is_master:
            if self.sps_task:
                self.sps_task.cancel()

            if self.sps2_task and gdata.configCommon.amount_of_propeller == 2:
                self.sps2_task.cancel()
        elif self.hmi_server_task:
            self.hmi_server_task.cancel()

        if gdata.configCommon.enable_gps and self.gps_task:
            self.gps_task.cancel()

    async def __read_plc_data(self):
        while self.task_running:
            try:
                if self.plc_log is None or self.plc_log.page is None:
                    return

                if plc.is_online:
                    content_parts = [
                        f"4-20mA: {await plc.read_4_20_ma_data()}",
                        f"instant data: {await plc.read_instant_data()}",
                        f"overload: {await plc.read_power_overload()}",
                        f"alarm: {await plc.read_alarm()}",
                        f"eexi breach: {await plc.read_eexi_breach_alarm()}"
                    ]

                    content = ", ".join(content_parts)

                    self.plc_log.controls.append(ft.Text(content))
                else:
                    self.plc_log.controls.append(ft.Text("disconnected from PLC"))

                self.plc_log.update()
            except:
                logging.exception('exception occured at SelfTest.__read_plc_data')
            finally:
                await asyncio.sleep(2)

    async def __read_gps_data(self):
        while self.task_running:
            try:
                if gps.is_online:
                    self.gps_log.controls.append(ft.Text(f"GPS Data: {gdata.configGps.raw_data}"))
                else:
                    self.gps_log.controls.append(ft.Text("Disconnected from GPS"))
                self.gps_log.update()
            except:
                logging.exception('exception occured at SelfTest.__read_gps_data')
            finally:
                await asyncio.sleep(2)

    async def __read_sps_data(self):
        while self.task_running:
            try:
                sps_data = f'ad0={round(gdata.configSPS.ad0, 1)},ad1={round(gdata.configSPS.ad1, 1)},speed={round(gdata.configSPS.speed, 1)},torque={round(gdata.configSPS.torque, 1)},thrust={round(gdata.configSPS.thrust, 1)}'
                if sps_read_task.is_online:
                    self.sps_log.controls.append(ft.Text(f"SPS Data: {sps_data}"))
                else:
                    self.sps_log.controls.append(ft.Text('Disconnected from SPS'))
                self.sps_log.update()
            except:
                logging.exception('exception occured at SelfTest.__read_sps_data')
            finally:
                await asyncio.sleep(2)

    async def __read_sps2_data(self):
        while self.task_running:
            try:
                sps2_data = f'ad0={round(gdata.configSPS2.ad0, 1)},ad1={round(gdata.configSPS2.ad1, 1)},speed={round(gdata.configSPS2.speed, 1)},torque={round(gdata.configSPS2.torque, 1)},thrust={round(gdata.configSPS2.thrust, 1)}'
                if sps2_read_task.is_online:
                    self.sps2_log.controls.append(ft.Text(f"SPS-2 Data: {sps2_data}"))
                else:
                    self.sps2_log.controls.append(ft.Text('Disconnected from SPS-2'))
                self.sps2_log.update()
            except:
                logging.exception('exception occured at SelfTest.__read_sps2_data')
            finally:
                await asyncio.sleep(2)

    async def __read_hmi_server_data(self):
        while self.task_running:
            try:
                if ws_client.is_online:
                    sps_data = f'sps: torque={gdata.configSPS.torque}, thrust={gdata.configSPS.thrust}, speed={gdata.configSPS.speed}'
                    self.hmi_server_log.controls.append(ft.Text(f"HMI Server Data: {sps_data}"))
                    if gdata.configCommon.amount_of_propeller == 2:
                        sps2_data = f'sps2: torque={gdata.configSPS2.torque}, thrust={gdata.configSPS2.thrust}, speed={gdata.configSPS2.speed}'
                        self.hmi_server_log.controls.append(ft.Text(f"HMI Server Data: {sps2_data}"))
                else:
                    self.hmi_server_log.controls.append(ft.Text(f"Disconnected from HMI Server."))
                self.hmi_server_log.update()
            except:
                logging.exception('exception occured at SelfTest.__read_hmi_server_data')
            finally:
                await asyncio.sleep(2)
