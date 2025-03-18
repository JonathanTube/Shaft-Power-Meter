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

right_content = ft.Container(
    expand=True,
    padding=ft.padding.only(left=5, right=5, top=5, bottom=5),
    content=SystemConf().create()
)


def _set_content(e):
    idx = e.control.selected_index
    if idx == 0:
        right_content.content = SystemConf().create()
    elif idx == 1:
        right_content.content = General().create()
    elif idx == 2:
        right_content.content = PropellerConf().create()
    elif idx == 3:
        right_content.content = ZeroCal.create()
    elif idx == 4:
        right_content.content = IO().create()
    elif idx == 5:
        right_content.content = Logs()
    elif idx == 6:
        right_content.content = createSelfTest()
    elif idx == 7:
        right_content.content = create_authority()
    elif idx == 8:
        right_content.content = create_data_dumping()

    right_content.update()


def createSetting():
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
                icon=ft.Icons.TAPAS_OUTLINED,
                selected_icon=ft.Icon(ft.Icons.TAPAS),
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
        on_change=_set_content
    )
    row = ft.Row(
        spacing=0,
        controls=[
            rail,
            ft.VerticalDivider(width=1),
            right_content
        ],
        expand=True
    )

    return row
