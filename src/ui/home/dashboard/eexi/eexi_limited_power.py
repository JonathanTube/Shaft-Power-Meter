import flet as ft
from ui.common.meter_half import MeterHalf


class EEXILimitedPower(ft.Card):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.margin = 0
        self.container_width = width
        self.container_height = height

        self.unlimited_power = 0
        self._task = None

    def build(self):
        meter_radius = self.container_width * 0.4
        self.meter_half = MeterHalf(radius=meter_radius)
        column = ft.Column(
            expand=True,
            spacing=self.container_height * 0.1,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    'EEXI Limited Power(%)',
                    weight=ft.FontWeight.BOLD,
                    size=20
                ),
                self.meter_half
            ])

        container = ft.Container(
            content=column,
            alignment=ft.alignment.center,
            padding=10,
            width=self.container_width + 10,
            height=self.container_height
        )

        self.content = container

    def set_config(self, normal: float, warning: float, unlimited: float):
        self.unlimited_power = normal
        green = normal
        orange = warning - normal
        red = unlimited - warning
        self.meter_half.set_inner_value(green, orange, red)

    def set_value(self, power: float):
        active_value = power
        inactive_value = self.unlimited_power - power
        self.meter_half.set_outer_value(active_value, inactive_value)
