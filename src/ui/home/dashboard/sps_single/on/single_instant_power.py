import flet as ft
from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser


class SingleInstantPower(ft.Container):
    def __init__(self):
        super().__init__()
        self.margin = 0
        self.expand = True

    def build(self):
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

    def set_value(self, value: float, unit: int):
        power = UnitParser.parse_power(value, unit)
        self.power_value.value = power[0]
        self.power_unit.value = power[1]
        self.content.update()