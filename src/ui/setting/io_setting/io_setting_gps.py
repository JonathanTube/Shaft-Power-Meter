import asyncio
import ipaddress
import logging
import flet as ft
from common.operation_type import OperationType
from db.models.io_conf import IOConf
from db.models.operation_log import OperationLog
from db.models.user import User
from task.gps_sync_task import gps_sync_task
from ui.common.custom_card import CustomCard
from ui.common.keyboard import keyboard
from ui.common.permission_check import PermissionCheck
from common.global_data import gdata

class IOSettingGPS(CustomCard):
    def __init__(self, conf: IOConf):
        super().__init__()
        self.conf = conf
        self.loop_task = None

    def build(self):
        self.gps_ip = ft.TextField(
            label=self.page.session.get("lang.setting.ip"),
            value=self.conf.gps_ip,
            read_only=True,
            col={"sm": 6},
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'ip')
        )

        self.gps_port = ft.TextField(
            label=self.page.session.get("lang.setting.port"),
            value=self.conf.gps_port,
            read_only=True,
            col={"sm": 6},
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'int')
        )

        self.connect_to_gps = ft.FilledButton(
            text=self.page.session.get("lang.setting.connect"),
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE,
            visible=not gdata.connected_to_gps,
            on_click=lambda e: self.page.open(PermissionCheck(self.__on_connect, 2))
        )

        self.disconnect_from_gps = ft.FilledButton(
            text=self.page.session.get("lang.setting.disconnect"),
            bgcolor=ft.Colors.RED,
            color=ft.Colors.WHITE,
            visible=gdata.connected_to_gps,
            on_click=lambda e: self.page.open(PermissionCheck(self.__on_disconnect, 2))
        )

        self.heading = self.page.session.get("lang.setting.gps_conf")
        self.body = ft.Row(controls=[self.gps_ip, self.gps_port, self.connect_to_gps, self.disconnect_from_gps])
        self.col = {"sm": 12}
        super().build()

    def __on_connect(self, user : User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.CONNECT_TO_GPS,
            operation_content=user.user_name
        )
        self.conf.gps_ip = self.gps_ip.value
        self.conf.gps_port = self.gps_port.value
        self.conf.save()

        self.page.run_task(self.__start_gps_task)
        
    
    async def __start_gps_task(self):
        try:
            self.connect_to_gps.text = self.page.session.get("lang.common.connecting")
            self.connect_to_gps.disabled = True
            self.connect_to_gps.update()
        
            await gps_sync_task.start(retry_once=True)
            self.__handle_gps_connection_status()
        except Exception as e:
            logging.exception(e)
    
    def __on_disconnect(self, user:User):
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.DISCONNECT_FROM_GPS,
            operation_content=user.user_name
        )
        self.page.run_task(self.__stop_gps_task)

    async def __stop_gps_task(self):
        try:
            await gps_sync_task.close_connection()
            self.__handle_gps_connection_status()
        except Exception as e:
            logging.exception(e)

    def save_data(self):
        try:
            ipaddress.ip_address(self.gps_ip.value)
        except ValueError:
            raise Exception(f'{self.page.session.get("lang.common.ip_address_format_error")}: {self.gps_ip.value}')

        self.conf.gps_ip = self.gps_ip.value
        self.conf.gps_port = self.gps_port.value


    def __handle_gps_connection_status(self):
        self.connect_to_gps.text = self.page.session.get("lang.setting.connect")
        self.connect_to_gps.visible = not gdata.connected_to_gps
        self.connect_to_gps.disabled = False
        self.connect_to_gps.update()

        self.disconnect_from_gps.visible = gdata.connected_to_gps
        self.disconnect_from_gps.update()

    def did_mount(self):
        self.loop_task = self.page.run_task(self.__handle_connection_status)

    async def __handle_connection_status(self):
        while True:
            await asyncio.sleep(1)
            try:
                if not self.connect_to_gps.disabled:
                    self.__handle_gps_connection_status()
            except Exception as e:
                logging.exception(e)

    def will_unmount(self):
        if self.loop_task:
            self.loop_task.cancel()
