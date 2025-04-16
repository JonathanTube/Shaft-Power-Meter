import flet as ft
from utils.unit_parser import UnitParser


class PowerLimited(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def build(self):
        self.title = ft.Text(self.page.session.get("lang.common.limited_power"), weight=ft.FontWeight.W_600)
        self.limited_power_value = ft.Text('0')
        self.limited_power_unit = ft.Text('W')

        self.content = ft.Container(
            padding=ft.padding.all(10),
            border=ft.border.all(
                width=0.5,
                color=ft.colors.with_opacity(0.15, ft.colors.INVERSE_SURFACE)
            ),
            border_radius=10,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    self.title,
                    ft.Row(controls=[
                        self.limited_power_value,
                        self.limited_power_unit
                    ])
                ]
            ))

    def set_value(self, value: float, unit: int):
        limited_power = UnitParser.parse_power(value, unit)
        self.limited_power_value.value = limited_power[0]
        self.limited_power_unit.value = limited_power[1]
        self.content.update()