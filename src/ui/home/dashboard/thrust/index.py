import logging
import flet as ft
from utils.unit_parser import UnitParser
from db.models.preference import Preference
from db.models.system_settings import SystemSettings
from common.global_data import gdata
from typing import Literal


class ThrustBlock(ft.Container):
    def __init__(self, name: Literal["sps", "sps2"]):
        super().__init__()
        self.right = 10
        self.top = 10
        self.name = name
        preference: Preference = Preference.get()
        self.system_unit = preference.system_unit
        system_settings: SystemSettings = SystemSettings.get()
        self.visible = system_settings.display_thrust

    def build(self):
        try:
            if self.page is None or self.page.session is None:
                return

            self.title = ft.Text(self.page.session.get("lang.common.thrust"), weight=ft.FontWeight.W_500, size=20)
            self.thrust_value = ft.Text("0")
            self.thrust_unit = ft.Text("N")
            self.content = ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.title,
                    ft.Row(controls=[self.thrust_value, self.thrust_unit])
                ],
                expand=True
            )
        except:
            logging.exception('exception occured at ThrustBlock.build')


    def reload(self):
        try:
            if self.content is None or self.content.page is None:
                return

            if self.name == "sps":
                thrust_and_unit = UnitParser.parse_thrust(gdata.sps_thrust, self.system_unit)
                self.thrust_value.value = thrust_and_unit[0]
                self.thrust_unit.value = thrust_and_unit[1]
            else:
                thrust_and_unit = UnitParser.parse_thrust(gdata.sps2_thrust, self.system_unit)
                self.thrust_value.value = thrust_and_unit[0]
                self.thrust_unit.value = thrust_and_unit[1]
            self.content.update()
        except:
            logging.exception('exception occured at ThrustBlock.reload')
