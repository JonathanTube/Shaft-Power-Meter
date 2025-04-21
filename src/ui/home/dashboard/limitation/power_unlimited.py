from ui.common.simple_card import SimpleCard
import flet as ft

from utils.unit_parser import UnitParser


class PowerUnlimited(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def build(self):
        self.title = ft.Text(self.page.session.get("lang.common.unlimited_power"), weight=ft.FontWeight.W_600)
        self.unlimited_power_value = ft.Text('0')
        self.unlimited_power_unit = ft.Text('W')

        self.content = ft.Container(
            border=ft.border.all(
                width=0.5,
                color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE)
            ),
            border_radius=10,
            padding=ft.padding.all(10),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    self.title,
                    ft.Row(controls=[
                        self.unlimited_power_value,
                        self.unlimited_power_unit
                    ])
                ]
            ))

    def set_value(self, value: float, unit: int):
        unlimited_power = UnitParser.parse_power(value, unit)
        self.unlimited_power_value.value = unlimited_power[0]
        self.unlimited_power_unit.value = unlimited_power[1]
        self.content.update()