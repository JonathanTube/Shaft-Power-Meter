import flet as ft

from ui.home.logs.breach import createBreachLog
from ui.home.logs.data import createDataLog
from ui.home.logs.gps import createGpsLog


def createLogs():
    return ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                text="Breach Log",
                content=ft.Container(
                    expand=True, bgcolor=ft.Colors.AMBER_300, content=createBreachLog())
            ),
            ft.Tab(
                text="Data Log",
                content=createDataLog()
            ),
            ft.Tab(
                text="GPS Log",
                content=createGpsLog()
            ),
        ],
        expand=True
    )
