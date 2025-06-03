import ipaddress
import flet as ft
from db.models.io_conf import IOConf
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard
from websocket.websocket_server import ws_server
from websocket.websocket_client import ws_client
from common.global_data import gdata

class IOSettingSPS(CustomCard):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf

    def build(self):
        self.connect_to_sps = ft.Checkbox(
            label=self.page.session.get("lang.setting.connect_to_sps"),
            value=self.conf.connect_to_sps,
            col={"sm": 6},
            on_change=lambda e: self.__connect_to_sps_changed(e)
        )

        self.start_server = ft.FilledButton(
            text=self.page.session.get("lang.setting.start_hmi_server"),
            col={"sm": 6},
            width=80,
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE,
            visible=self.conf.connect_to_sps and not gdata.hmi_server_started,
            on_click=lambda e: self.__start_hmi_server(e)
        )

        self.stop_server = ft.FilledButton(
            text=self.page.session.get("lang.setting.stop_hmi_server"),
            col={"sm": 6},
            width=80,
            bgcolor=ft.colors.RED,
            color=ft.colors.WHITE,
            visible=self.conf.connect_to_sps and gdata.hmi_server_started,
            on_click=lambda e: self.__stop_hmi_server(e)
        )

        self.sps1_ip = ft.TextField(
            label=f'{self.page.session.get("lang.setting.ip")} SPS1',
            value=self.conf.sps1_ip,
            read_only=True,
            col={"sm": 6},
            visible=self.conf.connect_to_sps,
            on_focus=lambda e: keyboard.open(e.control, 'ip')
        )

        self.sps1_port = ft.TextField(
            label=f'{self.page.session.get("lang.setting.port")} SPS1',
            value=self.conf.sps1_port,
            read_only=True,
            col={"sm": 6},
            visible=self.conf.connect_to_sps,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )

        self.sps2_ip = ft.TextField(
            label=f'{self.page.session.get("lang.setting.ip")} SPS2',
            value=self.conf.sps2_ip,
            read_only=True,
            col={"sm": 6},
            visible=self.conf.connect_to_sps,
            on_focus=lambda e: keyboard.open(e.control, 'ip')
        )

        self.sps2_port = ft.TextField(
            label=f'{self.page.session.get("lang.setting.port")} SPS2',
            value=self.conf.sps2_port,
            read_only=True,
            col={"sm": 6},
            visible=self.conf.connect_to_sps,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )

        self.connect_server = ft.FilledButton(
            text=self.page.session.get("lang.setting.connect_to_hmi_server"),
            bgcolor=ft.colors.GREEN,
            color=ft.colors.WHITE,
            col={"sm": 6},
            visible=not self.conf.connect_to_sps and not gdata.connected_to_hmi_server,
            on_click=lambda e: self.__connect_to_hmi_server(e)
        )

        self.disconnect_server = ft.FilledButton(
            text=self.page.session.get("lang.setting.disconnect_from_hmi_server"),
            bgcolor=ft.colors.RED,
            color=ft.colors.WHITE,
            col={"sm": 6},
            visible=not self.conf.connect_to_sps and gdata.connected_to_hmi_server,
            on_click=lambda e: self.__disconnect_from_hmi_server(e)
        )

        self.hmi_server_ip = ft.TextField(
            label=self.page.session.get("lang.setting.hmi_server_ip"),
            value=self.conf.hmi_server_ip,
            read_only=True,
            col={"sm": 6},
            visible=not self.conf.connect_to_sps,
        )

        self.hmi_server_port = ft.TextField(
            label=self.page.session.get("lang.setting.hmi_server_port"),
            value=self.conf.hmi_server_port,
            read_only=True,
            col={"sm": 6},
            visible=not self.conf.connect_to_sps,
        )

        self.heading = self.page.session.get("lang.setting.sps_conf")
        self.body = ft.ResponsiveRow(controls=[
            self.connect_to_sps, 
            self.start_server, self.stop_server,
            self.connect_server, self.disconnect_server,
            self.sps1_ip, self.sps1_port, self.sps2_ip, 
            self.sps2_port, self.hmi_server_ip, self.hmi_server_port
        ])
        self.col = {"sm": 12}
        super().build()

    def __start_hmi_server(self, e):
        self.page.run_task(self.handle_start_server)

    async def handle_start_server(self):
        started = await ws_server.start()
        self.start_server.visible = not started
        self.stop_server.visible = started
        self.start_server.update()
        self.stop_server.update()
        gdata.hmi_server_started = started

    def __stop_hmi_server(self, e):
        self.page.run_task(self.handle_stop_server)

    async def handle_stop_server(self):
        stopped = await ws_server.stop()
        self.start_server.visible = stopped
        self.stop_server.visible = not stopped
        self.start_server.update()
        self.stop_server.update()
        gdata.hmi_server_started = not stopped

    def __connect_to_hmi_server(self, e):
        self.page.run_task(self.handle_connect_to_hmi_server)

    async def handle_connect_to_hmi_server(self):
        connected = await ws_client.connect()
        self.connect_server.visible = not connected
        self.disconnect_server.visible = connected
        self.connect_server.update()
        self.disconnect_server.update()
        gdata.connected_to_hmi_server = connected

    def __disconnect_from_hmi_server(self, e):
        self.page.run_task(self.handle_disconnect_from_hmi_server)

    async def handle_disconnect_from_hmi_server(self):
        closed = await ws_client.close()
        self.connect_server.visible = closed
        self.disconnect_server.visible = not closed
        self.connect_server.update()
        self.disconnect_server.update()
        gdata.connected_to_hmi_server = not closed

    def __connect_to_sps_changed(self, e):
        is_connect_to_sps = e.control.value
        self.sps1_ip.visible = is_connect_to_sps
        self.sps1_port.visible = is_connect_to_sps
        self.sps2_ip.visible = is_connect_to_sps
        self.sps2_port.visible = is_connect_to_sps

        self.start_server.visible = is_connect_to_sps and not gdata.hmi_server_started
        self.stop_server.visible = is_connect_to_sps and gdata.hmi_server_started



        self.hmi_server_ip.visible = not is_connect_to_sps
        self.hmi_server_port.visible = not is_connect_to_sps

        self.connect_server.visible = not is_connect_to_sps and not gdata.connected_to_hmi_server
        self.disconnect_server.visible = not is_connect_to_sps and gdata.connected_to_hmi_server

        self.conf.connect_to_sps = e.control.value
        self.update()

    def save_data(self):
        try:
            ipaddress.ip_address(self.sps1_ip.value)
        except ValueError:
            raise Exception(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.sps1_ip.value}')

        try:
            ipaddress.ip_address(self.sps2_ip.value)
        except ValueError:
            raise Exception(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.sps2_ip.value}')

        self.conf.sps1_ip = self.sps1_ip.value
        self.conf.sps2_ip = self.sps2_ip.value

        self.conf.sps1_port = self.sps1_port.value
        self.conf.sps2_port = self.sps2_port.value
