import flet as ft

from ui.header.index import Header
from ui.home.index import createHome


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    pageContent = ft.Container(expand=True)

    page.appbar = Header(pageContent)

    pageContent.content = createHome()

    page.padding = ft.padding.only(left=20, right=20, top=0, bottom=20)
    page.add(pageContent)
    print('page.window.width=', page.window.width)
    print('page.width=', page.width)


ft.app(main)
