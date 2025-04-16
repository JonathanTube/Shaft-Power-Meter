import flet as ft

from ui.header.shapoli import ShaPoLi
from ui.header.logo import HeaderLogo
from ui.header.theme_button import ThemeButton
from ui.home.index import Home
from ui.report.report_info_list import ReportInfoList
from ui.setting.index import Setting
from task.test_mode_task import TestModeTask
from db.models.system_settings import SystemSettings


class Header(ft.AppBar):
    def __init__(self, main_content: ft.Container, test_mode_task: TestModeTask):
        super().__init__()
        self.test_mode_task = test_mode_task
        self.leading = HeaderLogo()
        self.title = ft.Text(value="Shaft Power Meter",
                             weight=ft.FontWeight.W_800)
        self.center_title = False
        self.bgcolor = ft.Colors.ON_INVERSE_SURFACE

        self.active_name = "HOME"
        self.main_content = main_content

        self.system_settings = SystemSettings.get()

    def build(self):
        self.home = ft.ElevatedButton(
            text="HOME",
            icon=ft.Icons.HOME_OUTLINED,
            icon_color=ft.Colors.WHITE,
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE_800,
            on_click=lambda e: self.on_click("HOME"))

        self.report = ft.ElevatedButton(
            text="REPORT",
            icon=ft.Icons.PICTURE_AS_PDF_OUTLINED,
            icon_color=ft.Colors.GREY_800,
            color=ft.Colors.GREY_800,
            bgcolor=ft.Colors.LIGHT_BLUE_100,
            on_click=lambda e: self.on_click("REPORT"))

        self.setting = ft.ElevatedButton(
            text="SETTING",
            icon=ft.Icons.SETTINGS_OUTLINED,
            icon_color=ft.Colors.GREY_800,
            color=ft.Colors.GREY_800,
            bgcolor=ft.Colors.LIGHT_BLUE_100,
            on_click=lambda e: self.on_click("SETTING"))

        self.actions = [
            ft.Container(
                content=ft.Row([self.home, self.report, self.setting]),
                margin=ft.margin.symmetric(horizontal=20)
            ),
            ShaPoLi(),
            ft.VerticalDivider(width=.5, thickness=.5),
            ThemeButton()
        ]

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

        if name == "HOME":
            self.main_content.content = Home()
            self.__set_active(self.home)
            self.__set_inactive(self.report)
            self.__set_inactive(self.setting)
        elif name == "REPORT":
            self.main_content.content = ReportInfoList()
            self.__set_inactive(self.home)
            self.__set_active(self.report)
            self.__set_inactive(self.setting)
        else:
            self.main_content.content = Setting(self.test_mode_task)
            self.__set_inactive(self.home)
            self.__set_inactive(self.report)
            self.__set_active(self.setting)

        self.active_name = name

        self.main_content.update()

    def on_system_settings_updated(self, topic, message):
        self.system_settings = SystemSettings.get()
        self.report.visible = self.system_settings.sha_po_li
        self.report.update()

    def did_mount(self):
        self.set_language()
        self.page.pubsub.subscribe_topic(
            "shapoli_conf_updated", self.on_system_settings_updated)

    def before_update(self):
        self.set_language()

    def set_language(self):
        self.title.value = self.page.session.get("lang.lang.app.name")
        self.home.text = self.page.session.get("lang.header.home")
        self.report.text = self.page.session.get("lang.header.report")
        self.setting.text = self.page.session.get("lang.header.setting")
