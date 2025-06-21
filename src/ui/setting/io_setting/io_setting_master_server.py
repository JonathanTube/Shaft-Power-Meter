import logging
import flet as ft
from common.operation_type import OperationType
from db.models.operation_log import OperationLog
from db.models.user import User
from ui.common.custom_card import CustomCard
from ui.common.permission_check import PermissionCheck
from websocket.websocket_server import ws_server
from common.global_data import gdata


class IOSettingMasterServer(CustomCard):
    def build(self):
        self.ip = ft.TextField(
            label=f'HMI {self.page.session.get("lang.setting.ip")}',
            value='0.0.0.0',
            read_only=True
        )

        self.port = ft.TextField(
            label=f'HMI {self.page.session.get("lang.setting.port")}',
            value='8000',
            read_only=True
        )

        self.start_hmi_server = ft.FilledButton(
            text=self.page.session.get("lang.setting.start_master_server"),
            bgcolor=ft.Colors.GREEN,
            color=ft.Colors.WHITE,
            visible=not gdata.master_server_started,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=5)
            ),
            on_click=lambda e: self.page.open(PermissionCheck(self.__start_server, 2))
        )

        self.stop_hmi_server = ft.FilledButton(
            text=self.page.session.get("lang.setting.stop_master_server"),
            bgcolor=ft.Colors.RED,
            color=ft.Colors.WHITE,
            visible=gdata.master_server_started,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=5)
            ),
            on_click=lambda e: self.page.open(PermissionCheck(self.__stop_server, 2))
        )

        self.heading = self.page.session.get("lang.setting.master_server_conf")

        self.body = ft.Row(controls=[
            self.ip,
            self.port,
            self.start_hmi_server,
            self.stop_hmi_server
        ])
        self.col = {"sm": 12}
        super().build()

    def __start_server(self, user: User):
        try:
            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.START_HMI_SERVER,
                operation_content=user.user_name
            )
            self.page.run_task(ws_server.start)
        except Exception as e:
            logging.exception(e)
        finally:
            self.__update_buttons()

    def __stop_server(self, user: User):
        try:
            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.STOP_HMI_SERVER,
                operation_content=user.user_name
            )
            self.page.run_task(ws_server.close)
        except Exception as e:
            logging.exception(e)
        finally:
            self.__update_buttons()

    def __update_buttons(self):
        self.start_hmi_server.visible = not gdata.master_server_started
        self.stop_hmi_server.visible = gdata.master_server_started
        self.start_hmi_server.update()
        self.stop_hmi_server.update()
