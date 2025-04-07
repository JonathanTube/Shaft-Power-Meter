import flet as ft

from ui.setting.authority import create_authority
from ui.setting.data_dumping import create_data_dumping
from ui.setting.general import General
from ui.setting.io import IO
from ui.setting.propeller_conf import PropellerConf
from ui.setting.self_test import createSelfTest
from ui.setting.system_conf import SystemConf
from ui.setting.zero_cal import ZeroCal

class Setting(ft.Container):
    def __init__(self):
        super().__init__()

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
            self.right_content.content = createSelfTest()
        elif idx == 6:
            self.right_content.content = create_authority()
        elif idx == 7:
            self.right_content.content = create_data_dumping()

        self.right_content.update()

    def build(self):
        self.right_content = ft.Container(
            expand=True,
            padding=10,
            content=SystemConf()
        )

        self.system_conf = ft.NavigationRailDestination(
            icon=ft.Icons.SETTINGS_OUTLINED,
            selected_icon=ft.Icons.SETTINGS,
            label="System Conf."
        )
        self.general = ft.NavigationRailDestination(
            icon=ft.Icon(ft.Icons.TUNE_OUTLINED),
            selected_icon=ft.Icon(ft.Icons.TUNE),
            label="General",
        )
        self.propeller_setting = ft.NavigationRailDestination(
            icon=ft.Icons.INSIGHTS_OUTLINED,
            selected_icon=ft.Icon(ft.Icons.INSIGHTS),
            label="Propeller Setting"
        )
        self.zero_cal = ft.NavigationRailDestination(
            icon=ft.Icons.SWITCH_ACCESS_SHORTCUT_OUTLINED,
            selected_icon=ft.Icon(ft.Icons.SWITCH_ACCESS_SHORTCUT),
            label="Zero Cal."
        )
        self.io_conf = ft.NavigationRailDestination(
            icon=ft.Icons.USB_OUTLINED,
            selected_icon=ft.Icon(ft.Icons.USB),
            label="I/O"
        )
        self.self_test = ft.NavigationRailDestination(
            icon=ft.Icons.ASSIGNMENT_OUTLINED,
            selected_icon=ft.Icon(ft.Icons.ASSIGNMENT),
            label="Self-test"
        )
        self.permission_conf = ft.NavigationRailDestination(
            icon=ft.Icons.MANAGE_ACCOUNTS_OUTLINED,
            selected_icon=ft.Icon(ft.Icons.MANAGE_ACCOUNTS),
            label="Permission Conf."
        )
        self.data_backup = ft.NavigationRailDestination(
            icon=ft.Icons.BACKUP_OUTLINED,
            selected_icon=ft.Icon(ft.Icons.BACKUP),
            label="Data Backup"
        )

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
                self.data_backup
            ],
            on_change=self.__set_content
        )
        self.content = ft.Row(
            spacing=0,
            controls=[
                rail,
                ft.VerticalDivider(width=1),
                self.right_content
            ],
            expand=True
        )

    def __set_language(self):
        session = self.page.session
        self.system_conf.label = session.get("lang.setting.system_conf.title")
        self.general.label = session.get("lang.setting.general.title")
        self.propeller_setting.label = session.get(
            "lang.setting.propeller_setting.title")
        self.zero_cal.label = session.get("lang.setting.zero_cal.title")
        self.io_conf.label = session.get("lang.setting.io_conf.title")
        self.self_test.label = session.get("lang.setting.self_test.title")
        self.permission_conf.label = session.get(
            "lang.setting.permission_conf.title")
        self.data_backup.label = session.get("lang.setting.data_backup.title")

    def before_update(self):
        self.__set_language()

    def did_mount(self):
        self.__set_language()
