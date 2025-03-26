import flet as ft
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser


class SpeedMeter(ft.Container):
    def __init__(self, max: float = 0, limit: float = 0, radius: int = 100):
        super().__init__()
        self.max = max
        self.limit = limit
        self.radius = radius

    def build(self):
        self.speed_meter = MeterRound(
            heading="Speed", radius=self.radius, unit="rpm"
        )
        self.content = self.speed_meter

    def did_mount(self):
        self.speed_meter.set_limitation(self.max, self.limit)

    def set_data(self, value: int):
        speed_and_unit = UnitParser.parse_speed(value)
        speed = speed_and_unit[0]
        unit = speed_and_unit[1]
        self.speed_meter.set_data(speed, unit)
