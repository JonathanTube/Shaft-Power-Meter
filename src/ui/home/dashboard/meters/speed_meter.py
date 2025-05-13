import flet as ft
from ui.common.meter_round import MeterRound
from common.global_data import gdata
from db.models.limitations import Limitations
from typing import Literal


class SpeedMeter(ft.Container):
    def __init__(self, name: Literal["sps1", "sps2"], radius: float):
        super().__init__()
        self.expand = False
        self.name = name
        self.radius = radius

    def build(self):
        limitations: Limitations = Limitations.get()
        max = limitations.speed_max
        limit = limitations.speed_warning

        heading = self.page.session.get("lang.common.speed")
        self.content = MeterRound(
            heading=heading, radius=self.radius, unit="rpm", max=max, limit=limit)

    def reload(self):
        if self.name == "sps1":
            self.content.set_data(gdata.sps1_speed, gdata.sps1_speed, "rpm")
        else:
            self.content.set_data(gdata.sps2_speed, gdata.sps2_speed, "rpm")
