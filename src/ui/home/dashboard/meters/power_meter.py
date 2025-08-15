import logging
import flet as ft
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser
from common.global_data import gdata
from typing import Literal


class PowerMeter(ft.Container):
    def __init__(self, name: Literal["sps", "sps2"], radius: float = 0):
        super().__init__()
        self.expand = False
        self.name = name
        self.radius = radius

    def build(self):
        try:
            if self.page is None or self.page.session is None:
                return

            max = gdata.configLimitation.power_max
            limit = gdata.configLimitation.power_warning

            heading = self.page.session.get("lang.common.power")
            self.content = MeterRound(heading=heading, radius=self.radius, unit="W", max=max, limit=limit)
        except:
            logging.exception('exception occured at PowerMeter.build')

    def reload(self):
        try:
            if self.content is None:
                return

            unit = gdata.configPreference.system_unit

            if self.name == "sps":
                if gdata.configSPS.power is not None:
                    power_and_unit = UnitParser.parse_power(gdata.configSPS.power, unit)
                    self.content.set_data(gdata.configSPS.power, power_and_unit[0], power_and_unit[1])
            else:
                if gdata.configSPS2.power is not None:
                    power_and_unit = UnitParser.parse_power(gdata.configSPS2.power, unit)
                    self.content.set_data(gdata.configSPS2.power, power_and_unit[0], power_and_unit[1])
        except:
            logging.exception('exception occured at PowerMeter.reload')
