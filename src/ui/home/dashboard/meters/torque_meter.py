import flet as ft
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser


class TorqueMeter(ft.Container):
    def __init__(self, radius: int = 100):
        super().__init__()
        self.expand = False
        self.radius = radius

    def build(self):
        self.torque = MeterRound(
            heading="Torque", radius=self.radius, unit="Nm"
        )
        self.content = self.torque

    def set_limit(self, max: float, limit: float):
        self.torque.set_limitation(max, limit)

    def set_data(self, value: float, unit: int):
        torque_and_unit = UnitParser.parse_torque(value, unit)
        self.torque.set_data(value, torque_and_unit[0], torque_and_unit[1])

    def set_language(self):
        session = self.page.session
        self.torque.heading = session.get("lang.common.torque")

    def did_mount(self):
        self.set_language()

    def before_update(self):
        self.set_language()
