import asyncio
import flet as ft
from common.global_data import gdata
from common.control_manager import ControlManager
from common.operation_type import OperationType
from db.models.date_time_conf import DateTimeConf
from db.models.operation_log import OperationLog
from db.models.user import User
from ui.common.permission_check import PermissionCheck
from ui.common.toast import Toast
from ui.header.shapoli import ShaPoLi
from ui.header.logo import HeaderLogo
from ui.header.theme import Theme
from ui.home.index import Home
from ui.report.report_info_list import ReportInfoList
from ui.setting.index import Setting
from db.models.system_settings import SystemSettings
from ui.common.keyboard import keyboard


class Header(ft.AppBar):
    def __init__(self, main_content: ft.Container):
        super().__init__()
        self.toolbar_height = 40
        self.leading = HeaderLogo()

        self.center_title = False
        self.bgcolor = ft.Colors.ON_INVERSE_SURFACE

        self.active_name = "HOME"
        self.main_content = main_content

    def build(self):
        self.system_settings = SystemSettings.get()
        self.title = ft.Text(value=self.page.session.get("lang.common.app_name"), weight=ft.FontWeight.W_700, size=20)

        self.utc_date_time = ft.Text()

        self.home = ft.ElevatedButton(
            text=self.page.session.get("lang.header.home"),
            icon=ft.Icons.HOME_OUTLINED,
            icon_color=ft.Colors.WHITE,
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_800,
            on_click=lambda e: self.on_click("HOME"))

        self.report = ft.ElevatedButton(
            text=self.page.session.get("lang.header.report"),
            icon=ft.Icons.PICTURE_AS_PDF_OUTLINED,
            icon_color=ft.Colors.GREY_800,
            color=ft.Colors.GREY_800,
            bgcolor=ft.Colors.LIGHT_BLUE_100,
            visible=self.system_settings.sha_po_li,
            on_click=lambda e: self.on_click("REPORT"))

        self.setting = ft.ElevatedButton(
            text=self.page.session.get("lang.header.setting"),
            icon=ft.Icons.SETTINGS_OUTLINED,
            icon_color=ft.Colors.GREY_800,
            color=ft.Colors.GREY_800,
            bgcolor=ft.Colors.LIGHT_BLUE_100,
            on_click=lambda e: self.on_click("SETTING"))

        self.shapoli = ShaPoLi()

        self.close_button = ft.IconButton(
            icon=ft.Icons.CLOSE_ROUNDED,
            on_click=lambda e: self.__close_app(e)
        )

        self.actions = [
            self.utc_date_time,
            ft.Container(
                content=ft.Row([self.home, self.report, self.setting]),
                margin=ft.margin.symmetric(horizontal=20)
            ),
            self.shapoli,
            ft.VerticalDivider(width=.5, thickness=.5),
            Theme(),
            ft.VerticalDivider(width=.5, thickness=.5),
            self.close_button
        ]

    def __close_app(self, e):
        self.page.open(PermissionCheck(self.__exit_app, 1))

    def __exit_app(self, user: User):
        user_id = user.id
        OperationLog.create(
            user_id=user_id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.SYSTEM_EXIT,
            operation_content=user.user_name
        )
        Toast.show_error(self.page, self.page.session.get("lang.toast.system_exit"))
        self.page.window.destroy()

    def __set_active(self, button: ft.ElevatedButton):
        button.bgcolor = ft.Colors.BLUE_800
        button.icon_color = ft.Colors.WHITE
        button.color = ft.Colors.WHITE
        button.update()

    def __set_inactive(self, button: ft.ElevatedButton):
        button.bgcolor = ft.Colors.LIGHT_BLUE_100
        button.icon_color = ft.Colors.GREY_800
        button.color = ft.Colors.GREY_800
        button.update()

    def on_click(self, name):
        if self.active_name == name:
            return

        keyboard.close()

        if name == "HOME":
            self.main_content.content = Home()
            self.__set_active(self.home)
            self.__set_inactive(self.report)
            self.__set_inactive(self.setting)
            ControlManager.home = self.main_content.content
        elif name == "REPORT":
            self.main_content.content = ReportInfoList()
            self.__set_inactive(self.home)
            self.__set_active(self.report)
            self.__set_inactive(self.setting)
            ControlManager.home = None
        else:
            self.main_content.content = Setting()
            self.__set_inactive(self.home)
            self.__set_inactive(self.report)
            self.__set_active(self.setting)
            ControlManager.home = None

        self.active_name = name

        self.main_content.update()

    async def sync_utc_date_time(self):
        datetime_conf: DateTimeConf = DateTimeConf.get()
        date_format = datetime_conf.date_format
        while True:
            self.utc_date_time.value = gdata.utc_date_time.strftime(f"{date_format} %H:%M:%S")
            self.utc_date_time.update()
            await asyncio.sleep(1)

    def did_mount(self):
        self.task = self.page.run_task(self.sync_utc_date_time)

    def will_unmount(self):
        if self.task:
            self.task.cancel()
