import flet as ft
from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser
from db.models.preference import Preference
from common.global_data import gdata


class SingleInstantTorque(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        preference: Preference = Preference.get()
        self.system_unit = preference.system_unit

    def build(self):
        self.torque_value = ft.Text(
            '0', size=18, width=80, text_align=ft.TextAlign.RIGHT
        )

        self.torque_unit = ft.Text(
            'Nm', size=18, width=50, text_align=ft.TextAlign.LEFT
        )
        self.content = SimpleCard(
            title=self.page.session.get("lang.common.torque"),
            body=ft.Row(
                tight=True,
                controls=[self.torque_value, self.torque_unit]
            )
        )

    def reload(self):
        torque = UnitParser.parse_torque(gdata.sps1_torque, self.system_unit)
        self.torque_value.value = torque[0]
        self.torque_unit.value = torque[1]
        self.content.update()
