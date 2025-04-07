import flet as ft


class PropellerCurveLegend(ft.Container):
    def __init__(self, normal_propeller_color: str, light_propeller_color: str,
                 speed_limit_color: str, torque_load_limit_color: str,
                 overload_color: str):
        super().__init__()
        self.expand = False
        self.bgcolor = ft.colors.ON_INVERSE_SURFACE
        self.border_radius = 10
        self.border_width = 1
        self.padding = 10
        self.left = 100

        self.normal_propeller_color = normal_propeller_color
        self.light_propeller_color = light_propeller_color
        self.speed_limit_color = speed_limit_color
        self.torque_load_limit_color = torque_load_limit_color
        self.overload_color = overload_color

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
                            width=22,
                            height=2,
                            bgcolor=self.normal_propeller_color
                        ),
                        ft.Text("Normal Propeller Curve",
                                color=self.normal_propeller_color)
                    ]
                ),
                ft.Row(
                    expand=False,
                    controls=[
                        ft.Text(
                            value="----",
                            weight=ft.FontWeight.BOLD,
                            color=self.light_propeller_color
                        ),
                        ft.Text("Light Propeller Curve",
                                color=self.light_propeller_color)
                    ]
                ),
                ft.Row(
                    expand=False,
                    controls=[
                        ft.Text(
                            value="······",
                            weight=ft.FontWeight.BOLD,
                            color=self.speed_limit_color
                        ),
                        ft.Text("Speed Limit Curve",
                                color=self.speed_limit_color)
                    ]
                ),
                ft.Row(
                    expand=False,
                    controls=[
                        ft.Container(
                            expand=False,
                            width=20,
                            height=2,
                            bgcolor=self.torque_load_limit_color
                        ),
                        ft.Text("Torque/Load Limit Curve",
                                color=self.torque_load_limit_color)
                    ]
                ),
                ft.Row(
                    expand=False,
                    controls=[
                        ft.Text(value="----",
                                weight=ft.FontWeight.BOLD,
                                color=self.overload_color),
                        ft.Text("Overload Curve", color=self.overload_color)
                    ]
                ),
                ft.Row(
                    expand=False,
                    controls=[
                        ft.Container(
                            expand=False,
                            width=10,
                            height=10,
                            border_radius=10,
                            bgcolor=ft.colors.ORANGE,
                            margin=ft.margin.symmetric(horizontal=6)
                        ),
                        ft.Text("sps1", color=ft.colors.ORANGE)
                    ]
                ),
                ft.Row(
                    expand=False,
                    controls=[
                        ft.Container(
                            expand=False,
                            width=10,
                            height=10,
                            border_radius=10,
                            bgcolor=ft.colors.LIME,
                            margin=ft.margin.symmetric(horizontal=6)
                        ),
                        ft.Text("sps2", color=ft.colors.LIME)
                    ]
                )
            ]
        )
