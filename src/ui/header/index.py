import flet as ft

from ui.header.shapoli import ShaPoLi
from ui.header.header_logo import HeaderLogo
from ui.header.header_menu import HeaderMenu
from ui.header.theme_button import ThemeButton


class Header(ft.AppBar):
    def __init__(self, content: ft.Container):
        super().__init__()
        self.leading = HeaderLogo()
        self.leading_width = 150
        self.title = ft.Text("Shaft Power Meter", weight=ft.FontWeight.W_800)
        self.center_title = False
        self.bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        self.actions = [
            ft.Container(
                content=HeaderMenu(content),
                margin=ft.margin.symmetric(horizontal=20)
            ),
            ft.VerticalDivider(width=1),
            ShaPoLi(),
            ft.VerticalDivider(width=1),
            ThemeButton()
        ]
