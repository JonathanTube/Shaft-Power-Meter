import logging
import flet as ft
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser
from common.global_data import gdata
from typing import Literal


class TorqueMeter(ft.Container):
    def __init__(self, name: Literal["sps", "sps2"], radius: float):
        super().__init__()
        self.expand = False
        self.name = name
        self.radius = radius

    def build(self):
        try:
            if self.page is None or self.page.session is None:
                return

            max = gdata.configLimitation.torque_max
            limit = gdata.configLimitation.torque_warning

            heading = self.page.session.get("lang.common.torque")
            self.content = MeterRound(heading=heading, radius=self.radius, unit="Nm", max=max, limit=limit)
        except:
            logging.exception('exception occured at TorqueMeter.build')

    def reload(self):
        try:
            if self.content is None:
                return

            unit = gdata.configPreference.system_unit
            if self.name == "sps":
                if gdata.configSPS.torque is not None:
                    torque_and_unit = UnitParser.parse_torque(gdata.configSPS.torque, unit)
                    self.content.set_data(gdata.configSPS.torque, torque_and_unit[0], torque_and_unit[1])
            else:
                if gdata.configSPS.torque is not None:
                    torque_and_unit = UnitParser.parse_torque(gdata.configSPS.torque, unit)
                    self.content.set_data(gdata.configSPS.torque, torque_and_unit[0], torque_and_unit[1])
        except:
            logging.exception('exception occured at TorqueMeter.reload')
