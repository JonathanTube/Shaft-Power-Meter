import flet as ft

from ui.common.custom_card import CustomCard
from .display import createDisplay


def createManually():
    return CustomCard(
        heading="Manually",
        expand=True,
        height=380,
        body=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                createDisplay(11, 22, 33, 44),
                ft.Text("Stopped", weight=ft.FontWeight.BOLD,
                        color=ft.Colors.RED_500),
                ft.Text("00 d 23:10:01 h measured"),
                ft.ElevatedButton("Start", color=ft.Colors.GREEN_500),
                ft.Text('stopped at 18/07/2014 06:56:19')
            ]))
