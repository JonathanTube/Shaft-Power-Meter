import flet as ft
from ui.common.meter_half import MeterHalf
from ui.common.simple_card import SimpleCard


class EEXILimitedPower(ft.Container):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.expand = True

        self.container_width = width
        self.container_height = height

        self.unlimited_power = 0
        self._task = None

    def build(self):
        meter_radius = self.container_width * 0.4
        self.meter_half = MeterHalf(radius=meter_radius)
        self.content = SimpleCard(
            title="EEXI Limited Power(%)",
            body=self.meter_half,
            text_center=True,
            body_bottom_right=False
        )

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
