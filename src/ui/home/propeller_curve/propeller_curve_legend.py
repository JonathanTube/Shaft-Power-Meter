import flet as ft

from db.models.system_settings import SystemSettings

class PropellerCurveLegend(ft.Container):
    def __init__(self, normal_propeller_color: str, light_propeller_color: str,
                 speed_limit_color: str, torque_load_limit_color: str,
                 overload_color: str):
        super().__init__()
        self.expand = False
        self.bgcolor = ft.Colors.ON_INVERSE_SURFACE
        self.border_radius = 10
        self.border_width = 1
        self.padding = 10
        self.top = 50
        self.left = 100

        self.normal_propeller_color = normal_propeller_color
        self.light_propeller_color = light_propeller_color
        self.speed_limit_color = speed_limit_color
        self.torque_load_limit_color = torque_load_limit_color
        self.overload_color = overload_color
        self.__load_config()

    def __load_config(self):
        self.system_setting = SystemSettings.get()

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
                            bgcolor=ft.Colors.RED,
                            border_radius=10,
                            margin=ft.margin.symmetric(horizontal=6)
                        ),
                        ft.Text(self.page.session.get('lang.propeller_curve.mcr_operating_point'), color=ft.Colors.RED)
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
                        ft.Text(self.page.session.get('lang.propeller_curve.normal_propeller_curve'), color=self.normal_propeller_color)
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
                        ft.Text(self.page.session.get('lang.propeller_curve.light_propeller_curve'), color=self.light_propeller_color)
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
                        ft.Text(self.page.session.get('lang.propeller_curve.speed_limit_curve'), color=self.speed_limit_color)
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
                        ft.Text(self.page.session.get('lang.propeller_curve.torque_load_limit_curve'), color=self.torque_load_limit_color)
                    ]
                ),
                ft.Row(
                    expand=False,
                    controls=[
                        ft.Text(value="----",
                                weight=ft.FontWeight.BOLD,
                                color=self.overload_color),
                        ft.Text(self.page.session.get('lang.propeller_curve.overload_curve'), color=self.overload_color)
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
                            bgcolor=ft.Colors.ORANGE,
                            margin=ft.margin.symmetric(horizontal=6)
                        ),
                        ft.Text('sps1', color=ft.Colors.ORANGE)
                    ]
                ),
                ft.Row(
                    expand=False,
                    visible=self.system_setting.amount_of_propeller == 2,
                    controls=[
                        ft.Container(
                            expand=False,
                            width=10,
                            height=10,
                            border_radius=10,
                            bgcolor=ft.Colors.LIME,
                            margin=ft.margin.symmetric(horizontal=6)
                        ),
                        ft.Text('sps2', color=ft.Colors.LIME)
                    ]
                )
            ]
        )
