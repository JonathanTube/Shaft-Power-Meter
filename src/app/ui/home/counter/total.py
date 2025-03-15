import flet as ft

from ...common.custom_card import create_card
from .display import createDisplay


def createTotal():
    return create_card(
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
