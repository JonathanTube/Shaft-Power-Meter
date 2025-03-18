import flet as ft


class FixedRight(ft.Container):
    def __init__(self):
        super().__init__()
        self.label_width = 120
        self.unit_width = 30
        self.content = self.__create()
        self.expand = False
        self.padding = ft.padding.only(left=5, right=5, top=5, bottom=5)
        self.animate = ft.animation.Animation(
            1000,
            ft.AnimationCurve.LINEAR_TO_EASE_OUT
        )
        self.border_radius = 10
        self.bgcolor = ft.colors.LIGHT_BLUE_500
        self.shadow = ft.BoxShadow(
            spread_radius=2,
            blur_radius=4,
            color=ft.colors.with_opacity(0.15, ft.colors.INVERSE_SURFACE),
            offset=ft.Offset(0, 1),
            blur_style=ft.ShadowBlurStyle.OUTER
        )
        self.on_hover = lambda e: self.__enlarge_fixed_right(e)
        self.right = 0
        self.top = 0

    def __create_thrust_power(self):
        self.thrust_label = ft.Text(
            "Thrust Power:",
            color=ft.colors.WHITE,
            width=self.label_width,
            text_align=ft.TextAlign.RIGHT,
            visible=False
        )
        thrust_value = ft.Text(
            "919192",
            color=ft.Colors.WHITE,
            text_align=ft.TextAlign.RIGHT
        )
        thrust_unit = ft.Text(
            "kN",
            color=ft.Colors.WHITE
        )
        return ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                self.thrust_label,
                thrust_value,
                thrust_unit
            ])

    def __create_unlimited_power(self):
        self.unlimited_power_label = ft.Text(
            "Unlimited Power:",
            color=ft.colors.WHITE,
            width=self.label_width,
            text_align=ft.TextAlign.RIGHT,
            visible=False
        )
        unlimited_power_value = ft.Text(
            '5555',
            color=ft.Colors.WHITE,
            text_align=ft.TextAlign.RIGHT
        )
        unlimited_power_unit = ft.Text(
            "kw",
            color=ft.Colors.WHITE
        )

        return ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                self.unlimited_power_label,
                unlimited_power_value,
                unlimited_power_unit
            ])

    def __create_limited_power(self):
        self.limited_power_label = ft.Text(
            "Limited Power:",
            color=ft.colors.WHITE,
            width=self.label_width,
            text_align=ft.TextAlign.RIGHT,
            visible=False
        )
        limited_power_value = ft.Text(
            '6666',
            color=ft.Colors.WHITE,
            text_align=ft.TextAlign.RIGHT
        )
        limited_power_unit = ft.Text(
            "kw",
            color=ft.Colors.WHITE
        )

        return ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                self.limited_power_label,
                limited_power_value,
                limited_power_unit
            ])

    def __enlarge_fixed_right(self, e):
        if e.data == "true":
            self.thrust_label.visible = True
            self.unlimited_power_label.visible = True
            self.limited_power_label.visible = True
        else:
            self.thrust_label.visible = False
            self.unlimited_power_label.visible = False
            self.limited_power_label.visible = False
        self.update()

    def __create(self):
        return ft.Column(
            controls=[
                self.__create_thrust_power(),
                self.__create_unlimited_power(),
                self.__create_limited_power()
            ]
        )


# def main(page: ft.Page):
#     page.add(
#         ft.Stack(
#             controls=[
#                 FixedRight()
#             ]
#         )
#     )


# ft.app(main)
