import flet as ft

from ui.setting.general import createGeneral
from ui.setting.propeller_setting import createPropellerSetting
from ui.setting.system_conf import createSystemConf

right_content = ft.Container(
    expand=True,
    padding=20,
    content=createSystemConf()
)


def _set_content(e):
    idx = e.control.selected_index
    if (idx == 0):
        right_content.content = createSystemConf()
    elif (idx == 1):
        right_content.content = createGeneral()
    elif (idx == 2):
        right_content.content = createPropellerSetting()
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
