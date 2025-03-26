import flet as ft
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser


class PowerMeter(ft.Container):
    def __init__(self, max: float, limit: float, radius: int = 130):
        super().__init__()
        self.max = max
        self.limit = limit
        self.radius = radius

    def build(self):
        self.power = MeterRound(heading="Power", radius=self.radius, unit="W")
        self.content = self.power

    def did_mount(self):
        self.power.set_limitation(self.max, self.limit)

    def set_data(self, value: float):
        power_and_unit = UnitParser.parse_power(value)
        power = power_and_unit[0]
        unit = power_and_unit[1]
        self.power.set_data(power, unit)
