import ipaddress
import logging
import flet as ft
from common.const_alarm_type import AlarmType
from db.models.io_conf import IOConf
from db.models.user import User
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard
from ui.common.permission_check import PermissionCheck
from ui.common.toast import Toast
from utils.alarm_saver import AlarmSaver
from websocket.websocket_slave import ws_client
from common.global_data import gdata


class InterfaceConf(ft.Container):
    def build(self):
        try:
            if self.page and self.page.session:
                self.connect_btn = ft.FilledButton(
                    text=self.page.session.get("lang.setting.connect_to_master"),
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    visible=False,
                    col={"sm": 4},
                    on_click=lambda e: self.page.open(PermissionCheck(self.__on_connect, 2))
                )

                self.close_btn = ft.FilledButton(
                    text=self.page.session.get("lang.setting.disconnect_from_master"),
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    visible=False,
                    col={"sm": 4},
                    on_click=lambda e: self.page.open(PermissionCheck(self.__on_close, 2))
                )

                self.hmi_server_ip = ft.TextField(
                    label=self.page.session.get("lang.setting.hmi_server_ip"),
                    value=gdata.configIO.hmi_server_ip,
                    read_only=True,
                    can_request_focus=False,
                    col={"sm": 4},
                    on_click=lambda e: keyboard.open(e.control, 'ip')
                )

                self.hmi_server_port = ft.TextField(
                    label=self.page.session.get("lang.setting.hmi_server_port"),
                    value=gdata.configIO.hmi_server_port,
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

    def __on_connect(self, user: User):
        try:
            self.save_data()
            gdata.configIO.set_default_value()
            if self.connect_btn and self.connect_btn.page:
                self.connect_btn.text = 'loading...'
                self.connect_btn.disabled = True
                self.connect_btn.bgcolor = ft.Colors.GREY
                self.connect_btn.update()
            self.page.run_task(ws_client.start)
        except Exception as e:
            Toast.show_error(self.page, str(e))

    def __on_close(self, user: User):
        try:
            if self.close_btn and self.close_btn.page:
                self.close_btn.text = 'loading...'
                self.close_btn.disabled = True
                self.close_btn.bgcolor = ft.Colors.GREY
                self.close_btn.update()
            self.page.run_task(ws_client.stop)
            AlarmSaver.create(AlarmType.SLAVE_MASTER, True)
        except:
            logging.exception("exception occured at InterfaceConf.__on_close")

    def save_data(self):
        try:
            ipaddress.ip_address(self.hmi_server_ip.value)
        except ValueError:
            raise ValueError(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.hmi_server_port.value}')

        hmi_server_ip = self.hmi_server_ip.value
        hmi_server_port = self.hmi_server_port.value
        IOConf.update(hmi_server_ip=hmi_server_ip, hmi_server_port=hmi_server_port).execute()

    def before_update(self):
        try:
            if self.page and self.page.session:
                if self.connect_btn:
                    self.connect_btn.visible = not ws_client.is_online
                    self.connect_btn.text = self.page.session.get("lang.setting.connect_to_master")
                    self.connect_btn.bgcolor = ft.Colors.GREEN
                    self.connect_btn.disabled = False

                if self.close_btn:
                    self.close_btn.visible = ws_client.is_online
                    self.close_btn.text = self.page.session.get("lang.setting.disconnect_from_master")
                    self.close_btn.bgcolor = ft.Colors.RED
                    self.close_btn.disabled = False
        except:
            logging.exception("exception occured at PropellerCurveDiagram.before_update")
