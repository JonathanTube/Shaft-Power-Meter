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

        self.task = None
        self.task_running = False

    def __set_content(self, e):
        idx = e.control.selected_index
        self.__switch_content(idx)
        if idx == 7:
            self.task_running = False

    def __switch_content(self, idx:int):
        try:
            if idx == self.idx:
                return

            self.idx = idx

            keyboard.close()

            if idx == 0:
                self.right_content.content = SystemConf()
            elif idx == 1:
                self.right_content.content = General()
            elif idx == 2:
                self.right_content.content = IOSetting()
            elif idx == 3:
                self.right_content.content = PropellerConf()
            elif idx == 4:
                self.right_content.content = ZeroCal()
            elif idx == 5:
                self.right_content.content = SelfTest()
            elif idx == 6:
                self.right_content.content = Permission()
            elif idx == 7:
                self.right_content.content = TestMode()
            
            self.right_content.update()
        except Exception:
            logging.exception("error occured while switch the button, please try it lately.")


    def build(self):
        self.right_content = ft.Container(
            expand=True,
            padding=ft.padding.only(left=10),
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

    def did_mount(self):
        self.task_running = True
        self.task = self.page.run_task(self.test_auto_run)
    
    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()

    async def test_auto_run(self):
        while self.task_running and gdata.auto_testing:
            idx = int(random() * 10) % len(self.rail.destinations)
            logging.info(f'&&&&&&&&&&&&&&-Setting.test_auto_run, idx = {idx}')
            self.__switch_content(idx=idx)
            self.rail.selected_index = idx
            self.rail.update()
            await asyncio.sleep(random())
        self.task_running = False