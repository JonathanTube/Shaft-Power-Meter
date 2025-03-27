import flet as ft


class PropellerCurveLegend(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = False
        self.bgcolor = ft.colors.SURFACE_CONTAINER_HIGHEST
        self.border_radius = 10
        self.border_width = 1
        self.padding = 10
        self.left = 100

    def build(self):
        self.content = ft.Column(
            expand=False,
            controls=[
                ft.Row(
                    expand=False,
                    controls=[
                        ft.Container(
                            expand=False,
                            width=10,
                            height=10,
                            bgcolor=ft.colors.RED,
                            border_radius=10,
                            margin=ft.margin.symmetric(horizontal=6)
                        ),
                        ft.Text("MCR Operating Point", color=ft.colors.RED)
                    ]
                ),
                ft.Row(
                    expand=False,
                    controls=[
                        ft.Container(
                            expand=False,
                            width=10,
                            height=10,
                            bgcolor=ft.colors.BLUE,
                            border_radius=10,
                            margin=ft.margin.symmetric(horizontal=6)
                        ),
                        ft.Text("SPS1", color=ft.colors.BLUE)
                    ]
                ),
                ft.Row(
                    expand=False,
                    controls=[
                        ft.Container(
                            expand=False,
                            width=10,
                            height=10,
                            bgcolor=ft.colors.GREEN,
                            border_radius=10,
                            margin=ft.margin.symmetric(horizontal=6)
                        ),
                        ft.Text("SPS2", color=ft.colors.GREEN)
                    ]
                ),
                ft.Row(
                    expand=False,
                    controls=[
                        ft.Container(
                            expand=False,
                            width=22,
                            height=2,
                            bgcolor=ft.colors.BLUE
                        ),
                        ft.Text("Normal Propeller Curve", color=ft.colors.BLUE)
                    ]
                ),
                ft.Row(
                    expand=False,
                    controls=[
                        ft.Text(
                            value="----",
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.BLUE
                        ),
                        ft.Text("Light Propeller Curve", color=ft.colors.BLUE)
                    ]
                ),
                ft.Row(
                    expand=False,
                    controls=[
                        ft.Text(
                            value="······",
                            weight=ft.FontWeight.BOLD,
                            color=ft.colors.RED
                        ),
                        ft.Text("Speed Limit Curve", color=ft.colors.RED)
                    ]
                ),
                ft.Row(
                    expand=False,
                    controls=[
                        ft.Container(
                            expand=False,
                            width=20,
                            height=2,
                            bgcolor=ft.colors.GREEN
                        ),
                        ft.Text("Torque/Load Limit Curve",
                                color=ft.colors.GREEN)
                    ]
                ),
                ft.Row(
                    expand=False,
                    controls=[
                        ft.Text(value="----",
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.RED),
                        ft.Text("Overload Curve", color=ft.colors.RED)
                    ]
                )
            ]
        )
