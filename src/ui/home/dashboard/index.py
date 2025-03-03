import flet as ft
from .power_line_chart import createPowerLineChart


def createDashboard():
    return ft.Column(
        spacing=20,
        controls=[
            ft.Container(expand=1, content=ft.Row(controls=[
                ft.Placeholder(
                    expand=True,
                    color=ft.Colors.random()  # random material color
                ),
                ft.Placeholder(
                    expand=True,
                    color=ft.Colors.random()  # random material color
                ),
                ft.Placeholder(
                    expand=True,
                    color=ft.Colors.random()  # random material color
                )
            ])),
            ft.Container(expand=3, content=createPowerLineChart())
        ]
    )
