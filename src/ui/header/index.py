import asyncio
import logging
import flet as ft
from random import random
from common.global_data import gdata
from ui.common.permission_check import PermissionCheck
from ui.common.toast import Toast
from ui.header.shapoli import ShaPoLi
from ui.header.logo import HeaderLogo
from ui.header.theme import Theme
from ui.common.keyboard import keyboard
from utils.system_exit_tool import SystemExitTool


class Header(ft.AppBar):
    def __init__(self, on_menu_click: callable):
        super().__init__()
        self.leading = HeaderLogo()

        self.on_menu_click = on_menu_click

        self.toolbar_height = 70
        self.leading_width = 70

        self.center_title = False
        self.bgcolor = ft.Colors.ON_INVERSE_SURFACE

        self.active_name = "HOME"

        self.task = None
        self.task_running = False

        self._auto_run_task = None
        self._auto_run_running = False

        self.is_switching = False

    def build(self):
        try:
            if self.page and self.page.session:
                self.app_name = ft.Text(value=self.page.session.get("lang.common.app_name"), weight=ft.FontWeight.W_700, size=20)
                self.title = self.app_name

                self.utc_date_time = ft.TextButton(
                    text="",
                    width=150,
                    style=ft.ButtonStyle(alignment=ft.alignment.center_left),
                    on_click=self.__stop_auto_testing
                )

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
                    on_click=lambda e: self.page.open(PermissionCheck(self.__on_exit, 1))
                )

                self.theme = Theme()

                self.actions = [
                    self.utc_date_time,
                    ft.Container(
                        content=ft.Row([self.home, self.report, self.setting]),
                        margin=ft.margin.symmetric(horizontal=20)
                    ),
                    self.shapoli,
                    ft.VerticalDivider(width=.5, thickness=.5),
                    self.theme,
                    ft.VerticalDivider(width=.5, thickness=.5),
                    self.close_button
                ]
        except:
            logging.exception('exception occured at Header.build')

    def __on_exit(self, user):
        asyncio.run(SystemExitTool.exit_app(self.page, user))

    def __stop_auto_testing(self, e):
        gdata.configTest.auto_testing = False

    def __set_active(self, button: ft.ElevatedButton):
        try:
            if button and button.page:
                button.bgcolor = ft.Colors.BLUE_800
                button.icon_color = ft.Colors.WHITE
                button.color = ft.Colors.WHITE
                button.update()
        except:
            logging.exception('exception occured at Header.__set_active')

    def __set_inactive(self, button: ft.ElevatedButton):
        try:
            if button and button.page:
                button.bgcolor = ft.Colors.LIGHT_BLUE_100
                button.icon_color = ft.Colors.GREY_800
                button.color = ft.Colors.GREY_800
                button.update()
        except:
            logging.exception('exception occured at Header.__set_inactive')

    def on_click(self, name):
        if self.is_switching:
            return

        if self.page is None:
            return

        if self.active_name == name:
            return

        try:
            self.is_switching = True

            keyboard.close()

            if name == "HOME":
                self.__set_active(self.home)
                self.__set_inactive(self.report)
                self.__set_inactive(self.setting)
            elif name == "REPORT":
                self.__set_inactive(self.home)
                self.__set_active(self.report)
                self.__set_inactive(self.setting)
            else:
                self.__set_inactive(self.home)
                self.__set_inactive(self.report)
                self.__set_active(self.setting)

            self.active_name = name

            if callable(self.on_menu_click):
                self.on_menu_click(name)

        except:
            logging.exception('exception occured at Header.on_click')
        finally:
            self.is_switching = False

    async def sync_utc_date_time(self):
        while self.task_running:
            try:
                if gdata.configDateTime.utc:
                    if self.utc_date_time and self.utc_date_time.page:
                        self.utc_date_time.text = gdata.configDateTime.utc.strftime(f"{gdata.configDateTime.date_format} %H:%M:%S")
                        self.utc_date_time.update()
            except:
                logging.exception('exception occured at Header.sync_utc_date_time')
            await asyncio.sleep(1)

    def before_update(self):
        try:
            if self.page and self.page.session:
                if self.report is not None:
                    self.report.visible = gdata.configCommon.shapoli

                if self.shapoli is not None:
                    self.shapoli.visible = gdata.configCommon.shapoli

                if self.app_name is not None:
                    self.app_name.value = self.page.session.get("lang.common.app_name")

                if self.home is not None:
                    self.home.text = self.page.session.get("lang.header.home")

                if self.report is not None:
                    self.report.text = self.page.session.get("lang.header.report")

                if self.setting is not None:
                    self.setting.text = self.page.session.get("lang.header.setting")
        except:
            logging.exception('exception occured at Header.before_update')

    def did_mount(self):
        try:
            self.task_running = True
            self.task = self.page.run_task(self.sync_utc_date_time)

            # 因为是60s多的切换时间，所以有足够时间，切换到testmode下，关闭或者打开自动化测试，所以这里一直开着
            self._auto_run_running = True
            self._auto_run_task = self.page.run_task(self.test_auto_run)
        except:
            logging.exception('exception occured at Header.did_mount')

    def will_unmount(self):
        try:
            self.task_running = False
            if self.task:
                self.task.cancel()

            self._auto_run_running = False
            if self._auto_run_task:
                self._auto_run_task.cancel()
        except:
            logging.exception('exception occured at Header.will_unmount')

    async def test_auto_run(self):
        arr = ['HOME', 'REPORT', 'SETTING']
        idx = 0
        while self._auto_run_running:
            try:
                if gdata.configTest.auto_testing:
                    # logging.info(f"&&&&&&&&&&&&&&-main menu auto testing, idx={idx}")
                    self.on_click(arr[idx % 3])
                    self.theme.toggle_theme()
                    idx += 1
                    # report没东西，2s够了
                    if self.active_name == 'REPORT':
                        await asyncio.sleep(1)
                    else:
                        await asyncio.sleep(random() * 5)
                else:
                    # 如果没有启动测试，自动间隔5s
                    await asyncio.sleep(5)
            except:
                return
