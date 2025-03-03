import flet as ft

from ui.header.index import Header
from ui.home.index import createHome


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    pageContent = ft.Container()

    page.appbar = Header(pageContent)

    pageContent.content = createHome()
    page.add(pageContent)


ft.app(main)
