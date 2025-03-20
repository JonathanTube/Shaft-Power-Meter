import flet as ft

from ui.setting.authority import create_authority
from ui.setting.data_dumping import create_data_dumping
from ui.setting.general import General
from ui.setting.io import IO
from ui.setting.logs.index import Logs
from ui.setting.propeller_conf import PropellerConf
from ui.setting.self_test import createSelfTest
from ui.setting.system_conf import SystemConf
from ui.setting.zero_cal import ZeroCal


class Setting(ft.Container):
    def __init__(self):
        super().__init__()
        self.right_content = ft.Container(
            expand=True,
            padding=ft.padding.only(left=5, right=5, top=5, bottom=5),
            content=SystemConf()
        )
        self.content = self.__create()

    def __set_content(self, e):
        idx = e.control.selected_index
        if idx == 0:
            self.right_content.content = SystemConf()
        elif idx == 1:
            self.right_content.content = General().create()
        elif idx == 2:
            self.right_content.content = PropellerConf().create()
        elif idx == 3:
            self.right_content.content = ZeroCal.create()
        elif idx == 4:
            self.right_content.content = IO().create()
        elif idx == 5:
            self.right_content.content = Logs()
        elif idx == 6:
            self.right_content.content = createSelfTest()
        elif idx == 7:
            self.right_content.content = create_authority()
        elif idx == 8:
            self.right_content.content = create_data_dumping()

        self.right_content.update()

    def __create(self):
        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="System Conf."
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.TUNE_OUTLINED),
                    selected_icon=ft.Icon(ft.Icons.TUNE),
                    label="General",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.INSIGHTS_OUTLINED,
                    selected_icon=ft.Icon(ft.Icons.INSIGHTS),
                    label="Propeller Setting"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SWITCH_ACCESS_SHORTCUT_OUTLINED,
                    selected_icon=ft.Icon(ft.Icons.SWITCH_ACCESS_SHORTCUT),
                    label="Zero Cal."
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.USB_OUTLINED,
                    selected_icon=ft.Icon(ft.Icons.USB),
                    label="I/O"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ABC_OUTLINED,
                    selected_icon=ft.Icon(ft.Icons.ABC),
                    label="Logs"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ASSIGNMENT_OUTLINED,
                    selected_icon=ft.Icon(ft.Icons.ASSIGNMENT),
                    label="Self-test"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.MANAGE_ACCOUNTS_OUTLINED,
                    selected_icon=ft.Icon(ft.Icons.MANAGE_ACCOUNTS),
                    label="Permission Conf."
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.BACKUP_OUTLINED,
                    selected_icon=ft.Icon(ft.Icons.BACKUP),
                    label="Data Dumping"
                )
            ],
            on_change=self.__set_content
        )
        return ft.Row(
            spacing=0,
            controls=[
                rail,
                ft.VerticalDivider(width=1),
                self.right_content
            ],
            expand=True
        )
