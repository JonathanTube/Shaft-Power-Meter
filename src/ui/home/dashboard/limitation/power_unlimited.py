from ui.common.simple_card import SimpleCard
import flet as ft

from utils.unit_parser import UnitParser


class PowerUnlimited(ft.Card):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.margin = 0

    def build(self):
        self.title = ft.Text("Un-limited Power", weight=ft.FontWeight.W_600)
        self.unlimited_power_value = ft.Text('0')
        self.unlimited_power_unit = ft.Text('W')

        self.content = ft.Container(
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

    def set_language(self):
        session = self.page.session
        self.title.value = session.get("lang.common.unlimited_power")

    def before_update(self):
        self.set_language()

    def did_mount(self):
        self.set_language()
