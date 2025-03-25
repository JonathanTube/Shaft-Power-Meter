import flet as ft
from utils.unit_parser import UnitParser


class PowerLimited(ft.Card):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.margin = 0

    def build(self):
        self.limited_power_value = ft.Text('0')
        self.limited_power_unit = ft.Text('W')

        self.content = ft.Container(
            padding=ft.padding.all(10),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Limited Power", weight=ft.FontWeight.W_600),
                    ft.Row(controls=[
                        self.limited_power_value,
                        self.limited_power_unit
                    ])
                ]
            ))

    def set_value(self, value: float):
        limited_power = UnitParser.parse_power(value)
        self.limited_power_value.value = limited_power[0]
        self.limited_power_unit.value = limited_power[1]
        self.content.update()
