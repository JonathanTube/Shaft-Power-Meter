import flet as ft


class FixedRight(ft.Container):
    def __init__(self):
        super().__init__()
        self.content = self.__create()
        self.expand = False
        self.padding = ft.padding.only(left=5, right=5, top=5, bottom=5)
        self.border_radius = 10
        self.shadow = ft.BoxShadow(
            spread_radius=2,
            blur_radius=4,
            color=ft.colors.with_opacity(0.15, ft.colors.INVERSE_SURFACE),
            offset=ft.Offset(0, 1),
            blur_style=ft.ShadowBlurStyle.OUTER
        )
        self.right = 0
        self.top = 0

    def __create_thrust_power(self):
        self.thrust_label = ft.Text(
            "Thrust Power:", weight=ft.FontWeight.W_500
        )
        thrust_value = ft.Text("919192")
        thrust_unit = ft.Text("kN")

        return ft.Column(
            controls=[
                self.thrust_label,
                ft.Row(controls=[
                    thrust_value,
                    thrust_unit
                ])
            ])

    def __create_unlimited_power(self):
        self.unlimited_power_label = ft.Text(
            "Unlimited Power:",
            weight=ft.FontWeight.W_500
        )
        unlimited_power_value = ft.Text('5555')
        unlimited_power_unit = ft.Text("kw")

        return ft.Column(
            controls=[
                self.unlimited_power_label,
                ft.Row(controls=[
                    unlimited_power_value,
                    unlimited_power_unit
                ])
            ])

    def __create_limited_power(self):
        self.limited_power_label = ft.Text(
            "Limited Power:", weight=ft.FontWeight.W_500
        )
        limited_power_value = ft.Text('6666')
        limited_power_unit = ft.Text("kw")

        return ft.Column(
            controls=[
                self.limited_power_label,
                ft.Row(controls=[
                    limited_power_value,
                    limited_power_unit
                ])
            ])

    def __create(self):
        return ft.Column(
            controls=[
                self.__create_thrust_power(),
                self.__create_unlimited_power(),
                self.__create_limited_power()
            ]
        )
