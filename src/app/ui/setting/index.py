import flet as ft

from .authority import create_authority
from .data_dumping import create_data_dumping
from .general import General
from .io import IO
from .propeller_conf import PropellerConf
from .self_test import createSelfTest
from .system_conf import SystemConf
from .zero_cal import ZeroCal

right_content = ft.Container(
    expand=True,
    padding=20,
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
        right_content.content = createSelfTest()
    elif idx == 6:
        right_content.content = create_authority()
    elif idx == 7:
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
        [
            rail,
            ft.VerticalDivider(width=1),
            right_content
        ],
        expand=True
    )

    return row
