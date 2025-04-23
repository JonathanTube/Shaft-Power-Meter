import flet as ft
from db.models.preference import Preference
from db.models.limitations import Limitations
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser
from common.global_data import gdata
from typing import Literal
from db.models.system_settings import SystemSettings


class PowerMeter(ft.Container):
    def __init__(self, name: Literal["sps1", "sps2"]):
        super().__init__()
        self.expand = False
        self.name = name
        preference: Preference = Preference.get()
        self.system_unit = preference.system_unit

        system_settings: SystemSettings = SystemSettings.get()
        self.amount_of_propeller = system_settings.amount_of_propeller

    def build(self):
        limitations: Limitations = Limitations.get()
        max = limitations.power_max
        limit = limitations.power_warning

        radius = self.page.window.height * 0.16
        if self.amount_of_propeller == 2:
            radius = radius * 0.75

        heading = self.page.session.get("lang.common.power")
        self.content = MeterRound(heading=heading, radius=radius, unit="W", max=max, limit=limit)

    def reload(self):
        if self.name == "sps1":
            power_and_unit = UnitParser.parse_power(gdata.sps1_power, self.system_unit)
            self.content.set_data(gdata.sps1_power, power_and_unit[0], power_and_unit[1])
        else:
            power_and_unit = UnitParser.parse_power(gdata.sps2_power, self.system_unit)
            self.content.set_data(gdata.sps2_power, power_and_unit[0], power_and_unit[1])
