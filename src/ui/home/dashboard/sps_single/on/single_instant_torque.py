import logging
import flet as ft
from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser
from common.global_data import gdata


class SingleInstantTorque(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def build(self):
        try:
            if self.page is None or self.page.session is None:
                return

            self.torque_value = ft.Text('0', size=18, width=80, text_align=ft.TextAlign.RIGHT)

            self.torque_unit = ft.Text('Nm', size=18, width=50, text_align=ft.TextAlign.LEFT)

            self.content = SimpleCard(
                title=self.page.session.get("lang.common.torque"),
                body=ft.Row(
                    tight=True,
                    controls=[self.torque_value, self.torque_unit]
                )
            )
        except:
            logging.exception('exception occured at SingleInstantTorque.build')

    def reload(self):
        try:
            if self.content and self.content.page:
                unit = gdata.configPreference.system_unit
                torque = UnitParser.parse_torque(gdata.configSPS.torque, unit)
                self.torque_value.value = torque[0]
                self.torque_unit.value = torque[1]
                if self.content and self.content.page:
                    self.content.update()
        except:
            logging.exception('exception occured at SingleInstantTorque.reload')
