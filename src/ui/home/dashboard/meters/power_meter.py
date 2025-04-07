import flet as ft
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser


class PowerMeter(ft.Container):
    def __init__(self, radius: int = 130):
        super().__init__()
        self.expand = False
        self.radius = radius

    def build(self):
        self.power = MeterRound(heading="Power", radius=self.radius, unit="W")
        self.content = self.power

    def set_limit(self, max: float, limit: float):
        self.power.set_limitation(max, limit)

    def set_data(self, value: float, unit: int):
        power_and_unit = UnitParser.parse_power(value, unit)
        power = power_and_unit[0]
        unit = power_and_unit[1]
        self.power.set_data(power, unit)

    def set_language(self):
        session = self.page.session
        self.power.heading = session.get("lang.common.power")

    def did_mount(self):
        self.set_language()

    def before_update(self):
        self.set_language()
