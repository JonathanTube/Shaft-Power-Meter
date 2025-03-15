import flet as ft

from .shapoli_button import ShaPoLiButton
from .header_logo import HeaderLogo
from .header_menu import HeaderMenu
from .theme_button import ThemeButton


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
            ShaPoLiButton(),
            ft.VerticalDivider(width=1),
            ThemeButton()
        ]
