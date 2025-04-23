import flet as ft
from ui.common.meter_round import MeterRound
from common.global_data import gdata
from db.models.limitations import Limitations
from typing import Literal
from db.models.system_settings import SystemSettings


class SpeedMeter(ft.Container):
    def __init__(self, name: Literal["sps1", "sps2"]):
        super().__init__()
        self.expand = False
        self.name = name

        system_settings: SystemSettings = SystemSettings.get()
        self.amount_of_propeller = system_settings.amount_of_propeller

    def build(self):
        limitations: Limitations = Limitations.get()
        max = limitations.speed_max
        limit = limitations.speed_warning

        radius = self.page.window.height * 0.14
        if self.amount_of_propeller == 2:
            radius = radius * 0.75

        heading = self.page.session.get("lang.common.speed")
        self.content = MeterRound(heading=heading, radius=radius, unit="rpm", max=max, limit=limit)

    def reload(self):
        if self.name == "sps1":
            self.content.set_data(gdata.sps1_speed, gdata.sps1_speed, "rpm")
        else:
            self.content.set_data(gdata.sps2_speed, gdata.sps2_speed, "rpm")
