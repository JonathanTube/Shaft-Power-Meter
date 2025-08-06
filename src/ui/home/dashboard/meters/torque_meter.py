import logging
import flet as ft
from ui.common.meter_round import MeterRound
from utils.unit_parser import UnitParser
from db.models.preference import Preference
from common.global_data import gdata
from db.models.limitations import Limitations
from typing import Literal


class TorqueMeter(ft.Container):
    def __init__(self, name: Literal["sps", "sps2"], radius: float):
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
            max = limitations.torque_max
            limit = limitations.torque_warning

            heading = self.page.session.get("lang.common.torque")
            self.content = MeterRound(heading=heading, radius=self.radius, unit="Nm", max=max, limit=limit)
        except:
            logging.exception('exception occured at TorqueMeter.build')

    def reload(self):
        try:
            if self.content is None:
                return

            if self.name == "sps":
                if gdata.configSPS.sps_torque is not None:
                    torque_and_unit = UnitParser.parse_torque(gdata.configSPS.sps_torque, self.system_unit)
                    self.content.set_data(gdata.configSPS.sps_torque, torque_and_unit[0], torque_and_unit[1])
            else:
                if gdata.configSPS.sps_torque is not None:
                    torque_and_unit = UnitParser.parse_torque(gdata.configSPS.sps_torque, self.system_unit)
                    self.content.set_data(gdata.configSPS.sps_torque, torque_and_unit[0], torque_and_unit[1])
        except:
            logging.exception('exception occured at TorqueMeter.reload')
