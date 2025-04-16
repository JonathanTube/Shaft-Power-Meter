import flet as ft
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser


class TorqueMeter(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = False

    def build(self):
        self.radius = self.page.window.height * 0.14
        self.torque = MeterRound(
            heading=self.page.session.get("lang.common.torque"), radius=self.radius, unit="Nm"
        )
        self.content = self.torque

    def set_limit(self, max: float, limit: float):
        self.torque.set_limitation(max, limit)

    def set_data(self, value: float, unit: int):
        torque_and_unit = UnitParser.parse_torque(value, unit)
        self.torque.set_data(value, torque_and_unit[0], torque_and_unit[1])
