import flet as ft
from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser


class SingleInstantThrust(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def build(self):
        self.thrust_value = ft.Text(
            '0', size=18, width=80, text_align=ft.TextAlign.RIGHT)
        self.thrust_unit = ft.Text(
            'N', size=18, width=50, text_align=ft.TextAlign.LEFT)
        self.content = SimpleCard(
            title="Thrust",
            body=ft.Row(
                tight=True,
                controls=[self.thrust_value, self.thrust_unit]
            )
        )

    def set_value(self, value: float, unit: int):
        thrust = UnitParser.parse_thrust(value, unit)
        self.thrust_value.value = thrust[0]
        self.thrust_unit.value = thrust[1]
        self.content.update()

    def set_language(self):
        session = self.page.session
        self.content.set_title(session.get("lang.common.thrust"))

    def before_update(self):
        self.set_language()

    def did_mount(self):
        self.set_language()
