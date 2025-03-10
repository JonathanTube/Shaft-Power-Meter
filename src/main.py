import flet as ft

from ui.header.index import Header
from ui.home.index import createHome


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page_content = ft.Container(expand=True)

    page.appbar = Header(page_content)

    page_content.content = createHome()

    page.padding = ft.padding.only(left=20, right=20, top=0, bottom=20)
<<<<<<< HEAD
    page.add(pageContent)
    print('page.window.width=', page.window.width)
    print('page.width=', page.width)
=======
    page.add(page_content)
>>>>>>> 964188027f679e6bf2547d31ef351cc106121048


ft.app(main)
