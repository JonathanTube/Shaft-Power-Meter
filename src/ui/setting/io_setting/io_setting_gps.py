import ipaddress
import logging
import flet as ft
from common.const_alarm_type import AlarmType
from db.models.io_conf import IOConf
from db.models.user import User
from task.gps_sync_task import gps
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard
from ui.common.permission_check import PermissionCheck
from common.global_data import gdata
from ui.common.toast import Toast
from utils.alarm_saver import AlarmSaver


class IOSettingGPS(ft.Container):
    def build(self):
        try:
            if self.page and self.page.session:
                self.gps_ip = ft.TextField(
                    label=self.page.session.get("lang.setting.ip"),
                    value=gdata.configIO.gps_ip,
                    read_only=True,
                    col={"sm": 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, 'ip')
                )

                self.gps_port = ft.TextField(
                    label=self.page.session.get("lang.setting.port"),
                    value=gdata.configIO.gps_port,
                    read_only=True,
                    col={"sm": 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, 'int')
                )

                self.connect_btn = ft.FilledButton(
                    text=self.page.session.get("lang.setting.connect"),
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                    visible=gps.is_online == None or gps.is_online == False,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    on_click=lambda e: self.page.open(PermissionCheck(self._on_connect, 2))
                )

                self.close_btn = ft.FilledButton(
                    text=self.page.session.get("lang.setting.disconnect"),
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    visible=gps.is_online == True,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    on_click=lambda e: self.page.open(PermissionCheck(self._on_close, 2))
                )

                self.custom_card = CustomCard(
                    self.page.session.get("lang.setting.gps_conf"),
                    ft.Row(controls=[
                        self.gps_ip,
                        self.gps_port,
                        self.connect_btn,
                        self.close_btn
                    ]),
                    col={"xs": 12})
                self.content = self.custom_card
        except:
            logging.exception('exception occured at IOSettingGPS.build')

    def _on_connect(self, user: User):
        try:
            self.save_data()
            gdata.configIO.set_default_value()
            if self.connect_btn and self.connect_btn.page:
                self.connect_btn.text = 'loading...'
                self.connect_btn.disabled = True
                self.connect_btn.bgcolor = ft.Colors.GREY
                self.connect_btn.update()
            self.page.run_task(gps.start)
        except Exception as e:
            Toast.show_error(self.page, str(e))

    def _on_close(self, user: User):
        try:
            if self.close_btn and self.close_btn.page:
                self.close_btn.text = 'loading...'
                self.close_btn.disabled = True
                self.close_btn.bgcolor = ft.Colors.GREY
                self.close_btn.update()

            self.page.run_task(gps.stop)
            AlarmSaver.create(AlarmType.MASTER_GPS)
        except:
            logging.exception("exception occured at IOSettingGPS.__on_close")

    def save_data(self):
        try:
            ipaddress.ip_address(self.gps_ip.value)
        except:
            raise ValueError(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.gps_ip.value}')
        gps_ip = self.gps_ip.value
        gps_port = self.gps_port.value
        IOConf.update(gps_ip=gps_ip, gps_port=gps_port).execute()

    def reset(self):
        try:
            if self.page and self.page.session:
                # 同步 GPS IP 和端口
                if self.gps_ip and self.gps_ip.page:
                    self.gps_ip.value = gdata.configIO.gps_ip

                if self.gps_port and self.gps_port.page:
                    self.gps_port.value = gdata.configIO.gps_port

                # 按钮状态同步
                if self.connect_btn and self.connect_btn.page:
                    self.connect_btn.visible = not gps.is_online
                    self.connect_btn.text = self.page.session.get("lang.setting.connect")
                    self.connect_btn.bgcolor = ft.Colors.GREEN
                    self.connect_btn.disabled = False

                if self.close_btn and self.close_btn.page:
                    self.close_btn.visible = gps.is_online
                    self.close_btn.text = self.page.session.get("lang.setting.disconnect")
                    self.close_btn.bgcolor = ft.Colors.RED
                    self.close_btn.disabled = False
        except:
            logging.exception("exception occured at IOSettingGPS.before_update")
