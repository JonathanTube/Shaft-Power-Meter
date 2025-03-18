import flet as ft

from ..home.index import create_home
from ..report.report_list import ReportList
from ..setting.index import createSetting


class HeaderMenu(ft.Row):
    def __init__(self, page_content: ft.Container):
        super().__init__()

        self.pageContent = page_content

        self.controls = [
            ft.FilledButton(text="HOME",
                            icon=ft.Icons.HOME_OUTLINED,
                            icon_color=ft.Colors.WHITE,
                            color=ft.Colors.WHITE,
                            bgcolor=ft.Colors.BLUE_800,
                            on_click=self.on_click),

            ft.ElevatedButton(text="REPORT",
                              icon=ft.Icons.REPORT_OUTLINED,
                              icon_color=ft.Colors.GREY_800,
                              color=ft.Colors.GREY_800,
                              bgcolor=ft.Colors.LIGHT_BLUE_100,
                              on_click=self.on_click),

            ft.ElevatedButton(text="SETTING",
                              icon=ft.Icons.SETTINGS_OUTLINED,
                              icon_color=ft.Colors.GREY_800,
                              color=ft.Colors.GREY_800,
                              bgcolor=ft.Colors.LIGHT_BLUE_100,
                              on_click=self.on_click)
        ]

        self.padding = 20

    def on_click(self, e):
        for control in self.controls:
            if e.control.text == control.text:
                control.bgcolor = ft.Colors.BLUE_800
                control.icon_color = ft.Colors.WHITE
                control.color = ft.Colors.WHITE
            else:
                control.bgcolor = ft.Colors.LIGHT_BLUE_100
                control.icon_color = ft.Colors.GREY_800
                control.color = ft.Colors.GREY_800
            control.update()

        if e.control.text == "HOME":
            self.pageContent.content = create_home()
        elif e.control.text == "REPORT":
            self.pageContent.content = ReportList().create()
        else:
            self.pageContent.content = createSetting()
        self.pageContent.update()
