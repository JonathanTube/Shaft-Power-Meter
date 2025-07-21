import logging
import flet as ft
from db.models.preference import Preference
from db.models.limitations import Limitations
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser
from common.global_data import gdata
from typing import Literal


class PowerMeter(ft.Container):
    def __init__(self, name: Literal["sps1", "sps2"], radius: float = 0):
        super().__init__()
        self.expand = False
        self.name = name
        self.radius = radius
        preference: Preference = Preference.get()
        self.system_unit = preference.system_unit

    def build(self):
        try:
            if self.page is None or self.page.session is None:
                return

            limitations: Limitations = Limitations.get()
            max = limitations.power_max
            limit = limitations.power_warning

            heading = self.page.session.get("lang.common.power")
            self.content = MeterRound(heading=heading, radius=self.radius, unit="W", max=max, limit=limit)
        except:
            logging.exception('exception occured at PowerMeter.build')

    def reload(self):
        try:
            if self.content is None:
                return
            

            if self.name == "sps1":
                if gdata.sps1_power is not None:
                    power_and_unit = UnitParser.parse_power(gdata.sps1_power, self.system_unit)
                    self.content.set_data(gdata.sps1_power, power_and_unit[0], power_and_unit[1])
            else:
                if gdata.sps2_power is not None:
                    power_and_unit = UnitParser.parse_power(gdata.sps2_power, self.system_unit)
                    self.content.set_data(gdata.sps2_power, power_and_unit[0], power_and_unit[1])
        except:
            logging.exception('exception occured at PowerMeter.reload')
