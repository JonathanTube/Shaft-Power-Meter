import asyncio
import logging
import flet as ft
from common.operation_type import OperationType
from db.models.operation_log import OperationLog
from db.models.user import User
from ui.common.custom_card import CustomCard
from ui.common.permission_check import PermissionCheck
from websocket.websocket_server import ws_server
from common.global_data import gdata


class IOSettingMasterServer(ft.Container):
    def __init__(self):
        super().__init__()
        self.loop_task = None
        self.task_running = False

    def build(self):
        try:
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

            self.start_btn = ft.FilledButton(
                text=self.page.session.get("lang.setting.start_master_server"),
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5)
                ),
                on_click=lambda e: self.page.open(PermissionCheck(self.on_start, 2))
            )

            self.stop_btn = ft.FilledButton(
                text=self.page.session.get("lang.setting.stop_master_server"),
                bgcolor=ft.Colors.RED,
                color=ft.Colors.WHITE,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=5)
                ),
                on_click=lambda e: self.page.open(PermissionCheck(self.on_stop, 2))
            )

            self.custom_card = CustomCard(
                self.page.session.get("lang.setting.master_server_conf"),
                ft.Row(controls=[
                    self.ip,
                    self.port,
                    self.start_btn,
                    self.stop_btn
                ])
            )
            self.content = self.custom_card
        except:
            logging.exception('exception occured at IOSettingMasterServer.build')

    def on_start(self, user: User):
        try:
            self.start_btn.text = "loading"
            self.start_btn.bgcolor = ft.Colors.GREY
            self.start_btn.disabled = True
            self.start_btn.update()

            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.START_HMI_SERVER,
                operation_content=user.user_name
            )
            self.page.run_task(ws_server.start)
        except:
            logging.exception('exception occured at IOSettingMasterServer.on_start')

    def on_stop(self, user: User):
        try:
            self.stop_btn.text = "loading"
            self.stop_btn.bgcolor = ft.Colors.GREY
            self.stop_btn.disabled = True
            self.stop_btn.update()

            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.STOP_HMI_SERVER,
                operation_content=user.user_name
            )
            self.page.run_task(ws_server.stop)
        except:
            logging.exception('exception occured at IOSettingMasterServer.on_stop')

    def before_update(self):
        self.start_btn.visible = not ws_server.is_started
        self.start_btn.text = self.page.session.get("lang.setting.start_master_server")
        self.start_btn.bgcolor = ft.Colors.GREEN
        self.start_btn.disabled = False

        self.stop_btn.visible = ws_server.is_started
        self.stop_btn.text = self.page.session.get("lang.setting.stop_master_server")
        self.stop_btn.bgcolor = ft.Colors.RED
        self.stop_btn.disabled = False

    async def __loop(self):
        while self.task_running:
            try:
                self.update()
            except:
                logging.exception("exception occured at IOSettingMasterServer.__loop")
                return
            finally:
                await asyncio.sleep(5)

    def did_mount(self):
        self.task_running = True
        self.loop_task = self.page.run_task(self.__loop)

    def will_unmount(self):
        self.task_running = False
        if self.loop_task:
            self.loop_task.cancel()
