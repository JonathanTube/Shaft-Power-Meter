import flet as ft
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser
from db.models.preference import Preference
from common.global_data import gdata
from db.models.limitations import Limitations
from typing import Literal


class TorqueMeter(ft.Container):
    def __init__(self, name: Literal["sps1", "sps2"], radius: float):
        super().__init__()
        self.expand = False
        self.name = name
        self.radius = radius
        preference: Preference = Preference.get()
        self.system_unit = preference.system_unit

    def build(self):
        limitations: Limitations = Limitations.get()
        max = limitations.torque_max
        limit = limitations.torque_warning

        heading = self.page.session.get("lang.common.torque")
        self.content = MeterRound(
            heading=heading, radius=self.radius, unit="Nm", max=max, limit=limit)

    def reload(self):
        if self.name == "sps1":
            torque_and_unit = UnitParser.parse_torque(
                gdata.sps1_torque, self.system_unit)
            self.content.set_data(
                gdata.sps1_torque, torque_and_unit[0], torque_and_unit[1])
        else:
            torque_and_unit = UnitParser.parse_torque(
                gdata.sps2_torque, self.system_unit)
            self.content.set_data(
                gdata.sps2_torque, torque_and_unit[0], torque_and_unit[1])
