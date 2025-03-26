import flet as ft
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser


class TorqueMeter(ft.Container):
    def __init__(self, max: float, limit: float, radius: int = 100):
        super().__init__()
        self.max = max
        self.limit = limit
        self.radius = radius

    def build(self):
        self.torque_meter = MeterRound(
            heading="Torque", radius=self.radius, unit="Nm")
        self.content = self.torque_meter

    def did_mount(self):
        self.torque_meter.set_limitation(self.max, self.limit)

    def set_data(self, value: float):
        torque_and_unit = UnitParser.parse_torque(value)
        torque = torque_and_unit[0]
        unit = torque_and_unit[1]
        self.torque_meter.set_data(torque, unit)
