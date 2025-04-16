import flet as ft
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser


class SpeedMeter(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = False

    def build(self):
        self.radius = self.page.window.height * 0.14
        self.speed = MeterRound(
            heading=self.page.session.get("lang.common.speed"), radius=self.radius, unit="rpm"
        )
        self.content = self.speed

    def set_limit(self, max: float, limit: float):
        self.speed.set_limitation(max, limit)

    def set_data(self, value: int):
        self.speed.set_data(value, value, "rpm")