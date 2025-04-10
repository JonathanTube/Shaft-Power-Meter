import flet as ft
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser


class SpeedMeter(ft.Container):
    def __init__(self, radius: int = 100):
        super().__init__()
        self.expand = False
        self.radius = radius

    def build(self):
        self.speed = MeterRound(
            heading="Speed", radius=self.radius, unit="rpm"
        )
        self.content = self.speed

    def set_limit(self, max: float, limit: float):
        self.speed.set_limitation(max, limit)

    def set_data(self, value: int):
        self.speed.set_data(value, value, "rpm")

    def set_language(self):
        session = self.page.session
        self.speed.heading = session.get("lang.common.speed")

    def did_mount(self):
        self.set_language()

    def before_update(self):
        self.set_language()
