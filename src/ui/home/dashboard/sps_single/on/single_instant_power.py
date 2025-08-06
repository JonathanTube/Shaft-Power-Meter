import logging
import flet as ft
from db.models.preference import Preference
from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser
from common.global_data import gdata


class SingleInstantPower(ft.Container):
    def __init__(self):
        super().__init__()
        self.margin = 0
        self.expand = True
        preference: Preference = Preference.get()
        self.system_unit = preference.system_unit

    def build(self):
        try:
            self.power_value = ft.Text(
                value='0', size=18, width=80,
                text_align=ft.TextAlign.RIGHT
            )
            self.power_unit = ft.Text(
                value='W', size=18, width=50,
                text_align=ft.TextAlign.LEFT
            )

            self.content = SimpleCard(
                title=self.page.session.get("lang.common.power"),
                body=ft.Row(
                    tight=True,
                    controls=[self.power_value, self.power_unit]
                )
            )
        except:
            logging.exception('exception occured at SingleInstantPower.build')



    def reload(self):
        try:
            power = UnitParser.parse_power(gdata.configSPS.sps_power, self.system_unit)
            self.power_value.value = power[0]
            self.power_unit.value = power[1]
            self.content.update()
        except:
            logging.exception('exception occured at SingleInstantPower.reload')
