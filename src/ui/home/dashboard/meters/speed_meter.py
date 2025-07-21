import logging
import flet as ft
from ui.common.meter_round import MeterRound
from common.global_data import gdata
from db.models.limitations import Limitations
from typing import Literal


class SpeedMeter(ft.Container):
    def __init__(self, name: Literal["sps", "sps2"], radius : float = 0):
        super().__init__()
        self.expand = False
        self.name = name
        self.radius = radius

    def build(self):
        try:
            if self.page is None or self.page.session is None:
                return

            limitations: Limitations = Limitations.get()
            max = limitations.speed_max
            limit = limitations.speed_warning

            heading = self.page.session.get("lang.common.speed")
            self.content = MeterRound(heading=heading, radius=self.radius, unit="rpm", max=max, limit=limit)
        except:
            logging.exception('exception occured at SpeedMeter.build')


    def reload(self):
        try:
            if self.content is None:
                return

            if self.name == "sps":
                if gdata.sps_speed is not None:
                    self.content.set_data(gdata.sps_speed, gdata.sps_speed, "rpm")
            else:
                if gdata.sps2_speed is not None:
                    self.content.set_data(gdata.sps2_speed, gdata.sps2_speed, "rpm")
        except:
            logging.exception('exception occured at SpeedMeter.reload')
