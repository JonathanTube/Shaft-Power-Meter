import flet as ft
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser


class PowerMeter(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = False

    def build(self):
        self.radius = self.page.window.height * 0.16
        self.power = MeterRound(heading=self.page.session.get("lang.common.power"), radius=self.radius, unit="W")
        self.content = self.power

    def set_limit(self, max: float, limit: float):
        # print(f"set_limit: {max}, {limit}")
        self.power.set_limitation(max, limit)

    def set_data(self, value: float, unit: int):
        power_and_unit = UnitParser.parse_power(value, unit)
        self.power.set_data(value, power_and_unit[0], power_and_unit[1])