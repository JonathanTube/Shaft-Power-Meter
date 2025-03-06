import flet as ft

from ui.common.custom_card import createCard
from ui.home.counter.display import createDisplay


def createTotal():
    return createCard(
        heading="Total",
        expand=True,
        height=380,
        body=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                createDisplay(11, 22, 33, 44),
                ft.Text("00 d 23:10:01 h measured"),
                ft.Text("started at 18/07/2014 06:56:19")
            ]))
