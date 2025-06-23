import ipaddress
import logging
import flet as ft
from common.operation_type import OperationType
from db.models.io_conf import IOConf
from db.models.operation_log import OperationLog
from db.models.user import User
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard
from ui.common.permission_check import PermissionCheck
from websocket.websocket_client import ws_client
from common.global_data import gdata


class InterfaceConf(ft.Container):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf: IOConf = conf

    def build(self):
        try:
            self.connect_btn = ft.FilledButton(
                text=self.page.session.get("lang.setting.connect_to_master"),
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5)
                ),
                col={"sm": 4},
                on_click=lambda e: self.page.open(PermissionCheck(self.__connect_to_master, 2))
            )

            self.close_btn = ft.FilledButton(
                text=self.page.session.get("lang.setting.disconnect_from_master"),
                bgcolor=ft.Colors.RED,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5)
                ),
                col={"sm": 4},
                on_click=lambda e: self.page.open(PermissionCheck(self.__disconnect_from_hmi_server, 2))
            )

            self.hmi_server_ip = ft.TextField(
                label=self.page.session.get("lang.setting.hmi_server_ip"),
                value=self.conf.hmi_server_ip,
                read_only=True,
                can_request_focus=False,
                col={"sm": 4},
                on_click=lambda e: keyboard.open(e.control, 'ip')
            )

            self.hmi_server_port = ft.TextField(
                label=self.page.session.get("lang.setting.hmi_server_port"),
                value=self.conf.hmi_server_port,
                read_only=True,
                can_request_focus=False,
                col={"sm": 4},
                on_click=lambda e: keyboard.open(e.control, 'int')
            )

            self.custom_card = CustomCard(
                self.page.session.get("lang.setting.interface_conf"),
                ft.Row(controls=[
                    self.hmi_server_ip,
                    self.hmi_server_port,
                    self.connect_btn,
                    self.close_btn
                ]))
            self.content = self.custom_card
        except:
            logging.exception('exception occured at InterfaceConf.build')

    def __connect_to_master(self, user: User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.CONNECT_TO_MASTER,
            operation_content=user.user_name
        )
        self.hmi_server_ip = self.hmi_server_ip.value
        self.hmi_server_port = self.hmi_server_port.value
        self.conf.save()
        self.page.run_task(self.handle_connect_to_master)

    async def handle_connect_to_master(self):
        try:
            self.connect_btn.text = self.page.session.get(
                "lang.common.connecting")
            self.connect_btn.disabled = True
            self.connect_btn.update()
            connected = await ws_client.connect()
            # recovery
            self.connect_btn.text = self.page.session.get(
                "lang.setting.connect_to_master")
            self.connect_btn.disabled = False
            self.connect_btn.visible = not connected
            self.connect_btn.update()

            self.close_btn.visible = connected
            self.close_btn.update()
        except Exception as e:
            logging.exception(e)

    def __disconnect_from_hmi_server(self, user: User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.DISCONNECT_FROM_HMI_SERVER,
            operation_content=user.user_name
        )
        self.page.run_task(self.handle_disconnect_from_hmi_server)

    async def handle_disconnect_from_hmi_server(self):
        try:
            closed = await ws_client.close()
            self.connect_btn.visible = closed
            self.close_btn.visible = not closed
            self.connect_btn.update()
            self.close_btn.update()
        except Exception as e:
            logging.exception(e)

    def save_data(self):
        try:
            ipaddress.ip_address(self.hmi_server_ip.value)
            self.conf.hmi_server_ip = self.hmi_server_ip.value
            self.conf.hmi_server_port = self.hmi_server_port.value
        except ValueError:
            raise ValueError(
                f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.hmi_server_port.value}')

    def before_update(self):
        self.connect_btn.visible = not ws_client.is_connected
        self.connect_btn.text = self.page.session.get(
            "lang.setting.connect_to_master")
        self.connect_btn.bgcolor = ft.Colors.GREEN
        self.connect_btn.disabled = False

        self.close_btn.visible = ws_client.is_connected
        self.close_btn.text = self.page.session.get(
            "lang.setting.disconnect_from_master")
        self.close_btn.bgcolor = ft.Colors.RED
        self.close_btn.disabled = False
