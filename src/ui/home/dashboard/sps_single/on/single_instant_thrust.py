import logging
import flet as ft
from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser
from db.models.preference import Preference
from common.global_data import gdata


class SingleInstantThrust(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        preference: Preference = Preference.get()
        self.system_unit = preference.system_unit
        self.visible = gdata.configCommon.show_thrust

    def build(self):
        try:
            self.thrust_value = ft.Text(
                '0', size=18, width=80, text_align=ft.TextAlign.RIGHT)
            self.thrust_unit = ft.Text(
                'N', size=18, width=50, text_align=ft.TextAlign.LEFT)
            self.content = SimpleCard(
                title=self.page.session.get("lang.common.thrust"),
                body=ft.Row(
                    tight=True,
                    controls=[self.thrust_value, self.thrust_unit]
                )
            )
        except:
            logging.exception('exception occured at SingleInstantThrust.build')

    def reload(self):
        try:
            thrust = UnitParser.parse_thrust(gdata.configSPS.thrust, self.system_unit)
            self.thrust_value.value = thrust[0]
            self.thrust_unit.value = thrust[1]
            if self.content and self.content.page:
                self.content.update()
        except:
            logging.exception('exception occured at SingleInstantThrust.reload')
