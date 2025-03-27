import flet as ft

from ui.header.shapoli import ShaPoLi
from ui.header.header_logo import HeaderLogo
from ui.header.header_menu import HeaderMenu
from ui.header.theme_button import ThemeButton


class Header(ft.AppBar):
    def __init__(self, content: ft.Container):
        super().__init__()
        self.leading = HeaderLogo()
        self.title = ft.Text("Shaft Power Meter", weight=ft.FontWeight.W_800)
        self.center_title = False
        self.bgcolor = ft.Colors.ON_INVERSE_SURFACE
        self.actions = [
            ft.Container(
                content=HeaderMenu(content),
                margin=ft.margin.symmetric(horizontal=20)
            ),
            ft.VerticalDivider(width=.5, thickness=.5),
            ShaPoLi(),
            ft.VerticalDivider(width=.5, thickness=.5),
            ThemeButton()
        ]
