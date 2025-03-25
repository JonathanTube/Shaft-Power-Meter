import flet as ft
from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser


class SingleInstantPower(ft.Container):
    def __init__(self):
        super().__init__()
        self.margin = 0
        self.expand = True

    def build(self):
        self.power_value = ft.Text('0', size=18)
        self.power_unit = ft.Text('W', size=18)

        self.content = SimpleCard(
            "Power",
            ft.Row(
                tight=True,
                controls=[self.power_value, self.power_unit]
            )
        )

    def set_value(self, value: float):
        power = UnitParser.parse_power(value)
        self.power_value.value = power[0]
        self.power_unit.value = power[1]
        self.content.update()
