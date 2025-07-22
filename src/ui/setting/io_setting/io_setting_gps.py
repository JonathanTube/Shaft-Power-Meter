import ipaddress
import logging
import flet as ft
from common.const_alarm_type import AlarmType
from common.operation_type import OperationType
from db.models.io_conf import IOConf
from db.models.operation_log import OperationLog
from db.models.user import User
from task.gps_sync_task import gps
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard
from ui.common.permission_check import PermissionCheck
from common.global_data import gdata
from ui.common.toast import Toast
from utils.alarm_saver import AlarmSaver


class IOSettingGPS(ft.Container):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf

    def build(self):
        try:
            if self.page and self.page.session:
                self.gps_ip = ft.TextField(
                    label=self.page.session.get("lang.setting.ip"),
                    value=self.conf.gps_ip,
                    read_only=True,
                    col={"sm": 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, 'ip')
                )

                self.gps_port = ft.TextField(
                    label=self.page.session.get("lang.setting.port"),
                    value=self.conf.gps_port,
                    read_only=True,
                    col={"sm": 4},
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, 'int')
                )

                self.connect_btn = ft.FilledButton(
                    text=self.page.session.get("lang.setting.connect"),
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                    visible=False,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    on_click=lambda e: self.page.open(PermissionCheck(self.__on_connect, 2))
                )

                self.close_btn = ft.FilledButton(
                    text=self.page.session.get("lang.setting.disconnect"),
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    visible=False,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=5)
                    ),
                    on_click=lambda e: self.page.open(PermissionCheck(self.__on_close, 2))
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

    def __on_connect(self, user: User):
        try:
            self.save_data()
            self.conf.save()
        except Exception as e:
            Toast.show_error(self.page, str(e))
            return

        try:
            self.connect_btn.text = 'loading...'
            self.connect_btn.disabled = True
            self.connect_btn.bgcolor = ft.Colors.GREY
            self.connect_btn.update()

            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.CONNECT_TO_GPS,
                operation_content=user.user_name
            )
            self.page.run_task(gps.connect)
        except:
            logging.exception("exception occured at IOSettingGPS.__on_connect")

    def __on_close(self, user: User):
        try:
            self.close_btn.text = 'loading...'
            self.close_btn.disabled = True
            self.close_btn.bgcolor = ft.Colors.GREY
            self.close_btn.update()

            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.DISCONNECT_FROM_GPS,
                operation_content=user.user_name
            )
            self.page.run_task(gps.close)
            AlarmSaver.create(alarm_type=AlarmType.MASTER_GPS_DISCONNECTED if gdata.is_master else AlarmType.SLAVE_GPS_DISCONNECTED)
        except:
            logging.exception("exception occured at IOSettingGPS.__on_close")

    def save_data(self):
        try:
            ipaddress.ip_address(self.gps_ip.value)
        except:
            raise ValueError(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.gps_ip.value}')

        self.conf.gps_ip = self.gps_ip.value
        self.conf.gps_port = self.gps_port.value

    def before_update(self):
        try:
            if self.page and self.page.session:
                if self.connect_btn:
                    self.connect_btn.visible = not gps.is_connected
                    self.connect_btn.text = self.page.session.get("lang.setting.connect")
                    self.connect_btn.bgcolor = ft.Colors.GREEN
                    self.connect_btn.disabled = False

                if self.close_btn:
                    self.close_btn.visible = gps.is_connected
                    self.close_btn.text = self.page.session.get("lang.setting.disconnect")
                    self.close_btn.bgcolor = ft.Colors.RED
                    self.close_btn.disabled = False
        except:
            logging.exception("exception occured at IOSettingGPS.before_update")
