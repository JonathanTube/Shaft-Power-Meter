import flet as ft
from utils.unit_parser import UnitParser
from ui.common.simple_card import SimpleCard


class SingleInstantSpeed(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def build(self):
        self.speed_value = ft.Text(
            '0', size=18, width=80, text_align=ft.TextAlign.RIGHT)
        self.speed_unit = ft.Text(
            'RPM', size=18, width=50, text_align=ft.TextAlign.LEFT)
        self.content = SimpleCard(
            title=self.page.session.get("lang.common.speed"),
            body=ft.Row(
                tight=True,
                controls=[self.speed_value, self.speed_unit]
            )
        )

    def set_value(self, value: float):
        speed = UnitParser.parse_speed(value)
        self.speed_value.value = speed[0]
        self.speed_value.update()
        self.speed_unit.value = speed[1]
        self.speed_unit.update()
