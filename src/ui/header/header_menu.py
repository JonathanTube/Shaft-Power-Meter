import flet as ft

from src.ui.home.index import createHome
from src.ui.report.report_list import ReportList
from src.ui.setting.index import createSetting


class HeaderMenu(ft.Row):
    def __init__(self, page_content: ft.Container):
        super().__init__()

        self.pageContent = page_content

        self.controls = [
            ft.ElevatedButton(text="HOME", icon=ft.Icons.HOME, color=ft.Colors.WHITE,
                              bgcolor=ft.Colors.BLUE_600, on_click=self.on_click),

            ft.ElevatedButton(text="REPORT", icon=ft.Icons.REPORT, color=ft.Colors.GREY_800,
                              bgcolor=None, on_click=self.on_click),

            ft.ElevatedButton(text="SETTING", icon=ft.Icons.SETTINGS, color=ft.Colors.GREY_800,
                              bgcolor=None, on_click=self.on_click)
        ]

        self.padding = 20

    def on_click(self, e):
        for control in self.controls:
            if e.control.text == control.text:
                control.bgcolor = ft.Colors.BLUE_600
                control.color = ft.Colors.WHITE
            else:
                control.bgcolor = None
                control.color = ft.Colors.GREY_800
            control.update()

        if e.control.text == "HOME":
            self.pageContent.content = createHome()
        elif e.control.text == "REPORT":
            self.pageContent.content = ReportList().create()
        else:
            self.pageContent.content = createSetting()
        self.pageContent.update()
