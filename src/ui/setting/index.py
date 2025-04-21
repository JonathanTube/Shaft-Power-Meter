import flet as ft

from ui.common.permission_check import PermissionCheck
from ui.setting.general.index import General
from ui.setting.io import IO
from ui.setting.propeller_conf import PropellerConf
from ui.setting.system_conf.index import SystemConf
from ui.setting.test_mode import TestMode
from ui.setting.zero_cal import ZeroCal
from ui.setting.self_test import SelfTest
from task.test_mode_task import TestModeTask
from ui.setting.permission.index import Permission


class Setting(ft.Container):
    def __init__(self, test_mode_task: TestModeTask):
        super().__init__()
        self.margin = ft.margin.all(10)
        self.test_mode_task = test_mode_task

    def __set_content(self, e):
        idx = e.control.selected_index
        if idx == 0:
            self.right_content.content = SystemConf()
        elif idx == 1:
            self.right_content.content = General()
        elif idx == 2:
            self.right_content.content = PropellerConf()
        elif idx == 3:
            self.right_content.content = ZeroCal.create()
        elif idx == 4:
            self.right_content.content = IO()
        elif idx == 5:
            self.right_content.content = SelfTest()
        elif idx == 6:
            self.page.open(PermissionCheck(self.__after_permission_check, 0, closable=False))
            self.right_content.content = None
        elif idx == 7:
            self.right_content.content = TestMode(self.test_mode_task)

        self.right_content.update()

    def __after_permission_check(self):
        self.right_content.content = Permission()
        self.right_content.update()

    def build(self):
        self.right_content = ft.Container(
            expand=True,
            padding=ft.padding.only(left=10),
            alignment=ft.alignment.top_left,
            content=SystemConf()
        )

        s = self.page.session
        self.system_conf = ft.NavigationRailDestination(icon=ft.Icons.SETTINGS_OUTLINED, selected_icon=ft.Icons.SETTINGS, label=s.get("lang.setting.system_conf.title"))
        self.general = ft.NavigationRailDestination(icon=ft.Icon(ft.Icons.TUNE_OUTLINED), selected_icon=ft.Icon(ft.Icons.TUNE), label=s.get("lang.setting.general.title"))
        self.propeller_setting = ft.NavigationRailDestination(icon=ft.Icons.INSIGHTS_OUTLINED, selected_icon=ft.Icon(ft.Icons.INSIGHTS), label=s.get("lang.setting.propeller_setting.title"))
        self.zero_cal = ft.NavigationRailDestination(icon=ft.Icons.SWITCH_ACCESS_SHORTCUT_OUTLINED, selected_icon=ft.Icon(ft.Icons.SWITCH_ACCESS_SHORTCUT), label=s.get("lang.setting.zero_cal.title"))
        self.io_conf = ft.NavigationRailDestination(icon=ft.Icons.USB_OUTLINED, selected_icon=ft.Icon(ft.Icons.USB), label=s.get("lang.setting.io_conf.title"))
        self.self_test = ft.NavigationRailDestination(icon=ft.Icons.ASSIGNMENT_OUTLINED, selected_icon=ft.Icon(ft.Icons.ASSIGNMENT), label=s.get("lang.setting.self_test.title"))
        self.permission_conf = ft.NavigationRailDestination(icon=ft.Icons.MANAGE_ACCOUNTS_OUTLINED, selected_icon=ft.Icon(ft.Icons.MANAGE_ACCOUNTS), label=s.get("lang.setting.permission_conf.title"))
        self.test_mode = ft.NavigationRailDestination(icon=ft.Icons.OUTLINED_FLAG, selected_icon=ft.Icon(ft.Icons.FLAG), label=s.get("lang.setting.test_mode.title"))

        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                self.system_conf,
                self.general,
                self.propeller_setting,
                self.zero_cal,
                self.io_conf,
                self.self_test,
                self.permission_conf,
                self.test_mode
            ],
            on_change=self.__set_content
        )
        self.content = ft.Row(
            spacing=0,
            controls=[rail, ft.VerticalDivider(width=1), self.right_content],
            expand=True
        )
