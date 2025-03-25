from ui.common.simple_card import SimpleCard
import flet as ft

from utils.unit_parser import UnitParser


class PowerUnlimited(ft.Card):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.margin = 0
        
    def build(self):
        self.unlimited_power_value = ft.Text('0')
        self.unlimited_power_unit = ft.Text('W')

        self.content = ft.Container(
            padding=ft.padding.all(10),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Text("Un-limited Power", weight=ft.FontWeight.W_600),
                    ft.Row(controls=[
                        self.unlimited_power_value,
                        self.unlimited_power_unit
                    ])
                ]
            ))

    def set_value(self, value: float):
        unlimited_power = UnitParser.parse_power(value)
        self.unlimited_power_value.value = unlimited_power[0]
        self.unlimited_power_unit.value = unlimited_power[1]
        self.content.update()
