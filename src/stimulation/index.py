import flet as ft
from gps_server import gps_server
from modbus_server import modbus_server

class Stimulation(ft.Tabs):
    def __init__(self):
        super().__init__()

    def build(self):
        self.tabs = [
            ft.Tab(
                text="GPS",
                content=gps_server()
            ),
            ft.Tab(
                text="Modbus",
                content=modbus_server()
            )
        ]


async def main(page: ft.Page):
    page.title = "Stimulation Tool"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 800
    page.window.height = 600
    page.window.center()
    page.window.maximizable = False
    page.window.maximized = False
    page.window.resizable = False
    page.expand = True
    page.add(Stimulation())

ft.app(main)
