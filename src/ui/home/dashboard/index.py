import flet as ft

from .power_line_chart import createPowerLineChart


def createDashboard():
    return ft.Column(
        spacing=20,
        expand=True,
        controls=[
            ft.Container(content=ft.Row(controls=[
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
            ]),
                bgcolor=ft.Colors.GREEN_400),
            ft.Container(expand=True, content=createPowerLineChart(),
                         bgcolor=ft.Colors.BLUE_400),
        ])
