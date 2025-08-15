import asyncio
import logging
import flet as ft
from random import random
from ui.setting.general.index import General
from ui.setting.propeller_conf.index import PropellerConf
from ui.setting.self_test import SelfTest
from ui.setting.system_conf.index import SystemConf
from ui.setting.test_mode.index import TestMode
from ui.setting.zero_cal.index import ZeroCal
from ui.setting.permission.index import Permission
from ui.setting.io_setting.index import IOSetting
from ui.common.keyboard import keyboard
from common.global_data import gdata


class Setting(ft.Container):
    def __init__(self):
        super().__init__()
        self.margin = ft.margin.all(10)
        self.idx = 0

        self.is_switching = False

        self.task = None
        self.task_running = False

        self.rail = None

    def __set_content(self, e):
        idx = e.control.selected_index
        self.__switch_content(idx)

    def __switch_content(self, idx: int):
        if self.is_switching:
            return

        if idx == self.idx:
            return

        try:
            self.is_switching = True

            if self.page and self.right_content and self.right_content.page:

                self.idx = idx

                keyboard.close()

                if idx == 0:
                    self.right_content.content = self.content_system_conf
                elif idx == 1:
                    self.right_content.content = self.content_general
                elif idx == 2:
                    self.right_content.content = self.content_io_setting
                elif idx == 3:
                    self.right_content.content = self.content_propeller_conf
                elif idx == 4:
                    self.right_content.content = self.content_zero_cal
                elif idx == 5:
                    self.right_content.content = self.content_self_test
                elif idx == 6:
                    self.right_content.content = self.content_permission
                elif idx == 7:
                    self.right_content.content = self.content_test_mode

                if self.right_content and self.right_content.page:
                    self.right_content.update()
        except:
            logging.exception("error occured while switch the button, please try it lately.")
        finally:
            self.is_switching = False

    def build(self):
        try:
            self.content_system_conf = SystemConf()
            self.content_general = General()
            self.content_io_setting = IOSetting()
            self.content_propeller_conf = PropellerConf()
            self.content_zero_cal = ZeroCal()
            self.content_self_test = SelfTest()
            self.content_permission = Permission()
            self.content_test_mode = TestMode()

            if self.page and self.page.session:
                self.right_content = ft.Container(
                    expand=True,
                    padding=ft.padding.only(left=10, bottom=10, top=10, right=10),
                    alignment=ft.alignment.top_left,
                    content=SystemConf()
                )

                s = self.page.session
                self.system_conf = ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label=s.get("lang.setting.system_conf.title")
                )
                self.general = ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.TUNE_OUTLINED),
                    selected_icon=ft.Icon(ft.Icons.TUNE),
                    label=s.get("lang.setting.general.title")
                )
                self.propeller_conf = ft.NavigationRailDestination(
                    icon=ft.Icons.INSIGHTS_OUTLINED,
                    selected_icon=ft.Icon(ft.Icons.INSIGHTS),
                    label=s.get("lang.setting.propeller_setting.title")
                )

                self.zero_cal = ft.NavigationRailDestination(
                    icon=ft.Icons.SWITCH_ACCESS_SHORTCUT_OUTLINED,
                    selected_icon=ft.Icon(ft.Icons.SWITCH_ACCESS_SHORTCUT),
                    label=s.get("lang.setting.zero_cal.title")
                )
                self.io_conf = ft.NavigationRailDestination(
                    icon=ft.Icons.USB_OUTLINED,
                    selected_icon=ft.Icon(ft.Icons.USB),
                    label=s.get("lang.setting.io_conf.title")
                )
                self.self_test = ft.NavigationRailDestination(
                    icon=ft.Icons.ASSIGNMENT_OUTLINED,
                    selected_icon=ft.Icon(ft.Icons.ASSIGNMENT),
                    label=s.get("lang.setting.self_test.title")
                )
                self.permission_conf = ft.NavigationRailDestination(
                    icon=ft.Icons.MANAGE_ACCOUNTS_OUTLINED,
                    selected_icon=ft.Icon(ft.Icons.MANAGE_ACCOUNTS),
                    label=s.get("lang.setting.permission_conf.title")
                )
                self.test_mode = ft.NavigationRailDestination(
                    icon=ft.Icons.OUTLINED_FLAG,
                    selected_icon=ft.Icon(ft.Icons.FLAG),
                    label=s.get("lang.setting.test_mode.title")
                )

                self.rail = ft.NavigationRail(
                    selected_index=self.idx,
                    label_type=ft.NavigationRailLabelType.ALL,
                    destinations=[
                        self.system_conf,
                        self.general,
                        self.io_conf,
                        self.propeller_conf,
                        self.zero_cal,
                        self.self_test,
                        self.permission_conf,
                        self.test_mode
                    ],
                    on_change=self.__set_content
                )
                self.content = ft.Row(
                    spacing=0,
                    controls=[self.rail, ft.VerticalDivider(width=1), self.right_content],
                    expand=True
                )
        except:
            logging.exception('exception occured at Setting.build')

    def set_index_0(self):
        self.idx = 0
        if self.rail and self.rail.page:
            self.rail.selected_index = 0

    def before_update(self):
        try:
            if self.page and self.page.session:
                s = self.page.session
                self.system_conf.label = s.get("lang.setting.system_conf.title")
                self.general.label = s.get("lang.setting.general.title")
                self.propeller_conf.label = s.get("lang.setting.propeller_setting.title")
                self.zero_cal.label = s.get("lang.setting.zero_cal.title")
                self.io_conf.label = s.get("lang.setting.io_conf.title")
                self.self_test.label = s.get("lang.setting.self_test.title")
                self.permission_conf.label = s.get("lang.setting.permission_conf.title")
                self.test_mode.label = s.get("lang.setting.test_mode.title")
        except:
            logging.exception('exception occured at Setting.before_update')

    def did_mount(self):
        self.task_running = True
        self.task = self.page.run_task(self.test_auto_run)

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()

    async def test_auto_run(self):
        while self.task_running and gdata.configTest.auto_testing:
            try:
                idx = int(random() * 10) % len(self.rail.destinations)
                # logging.info(f'&&&&&&&&&&&&&&-Setting.test_auto_run, idx = {idx}')
                self.__switch_content(idx=idx)
                self.rail.selected_index = idx
                self.rail.update()
                await asyncio.sleep(random())
            except:
                return
