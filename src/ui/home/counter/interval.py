import flet as ft

from ui.common.custom_card import CustomCard
from .display import createDisplay


def createInterval(propellerName: str):
    return CustomCard(
        heading=f"Interval({propellerName})" if propellerName else "Interval",
        expand=True,
        height=380,
        body=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                createDisplay(11, 22, 33, 44),

                ft.Text("00:20:12 left", weight=ft.FontWeight.BOLD,
                        bgcolor=ft.Colors.GREEN_200),

                ft.TextField(
                    label="Interval Setting",
                    suffix_text="h",
                    prefix_icon=ft.Icons.PUNCH_CLOCK_OUTLINED
                ),

                ft.Text("running 0.5h starting at 08:04")
            ]))
