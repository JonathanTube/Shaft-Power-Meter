import flet as ft
from utils.unit_parser import UnitParser


class ThrustPower(ft.Container):
    def __init__(self):
        super().__init__()
        self.right = 10
        self.top = 10

    def build(self):
        self.thrust_value = ft.Text("0")
        self.thrust_unit = ft.Text("W")
        self.content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Thrust Power", weight=ft.FontWeight.W_500),
                ft.Row(controls=[self.thrust_value, self.thrust_unit])
            ],
            expand=True
        )

    def set_data(self, value: float):
        thrust_and_unit = UnitParser.parse_power(value)
        self.thrust_value.value = thrust_and_unit[0]
        self.thrust_unit.value = thrust_and_unit[1]
        self.content.update()
