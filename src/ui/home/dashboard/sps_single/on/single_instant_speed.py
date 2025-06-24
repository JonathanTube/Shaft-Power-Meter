import logging
import flet as ft
from utils.unit_parser import UnitParser
from ui.common.simple_card import SimpleCard
from common.global_data import gdata


class SingleInstantSpeed(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def build(self):
        try:
            self.speed_value = ft.Text('0', size=18, width=80, text_align=ft.TextAlign.RIGHT)
            self.speed_unit = ft.Text('RPM', size=18, width=50, text_align=ft.TextAlign.LEFT)
            self.content = SimpleCard(
                title=self.page.session.get("lang.common.speed"),
                body=ft.Row(tight=True, controls=[self.speed_value, self.speed_unit])
            )
        except:
            logging.exception('exception occured at SingleInstantSpeed.build')

    def reload(self):
        try:
            speed = UnitParser.parse_speed(gdata.sps1_speed)
            self.speed_value.value = speed[0]
            self.speed_value.update()
            self.speed_unit.value = speed[1]
            self.speed_unit.update()
        except:
            logging.exception('exception occured at SingleInstantPower.reload')
