import flet as ft
from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser


class SingleInstantThrust(ft.Container):
    def __init__(self, visible: bool = True):
        super().__init__()
        self.expand = True
        self.visible = visible

    def build(self):
        self.thrust_value = ft.Text('0', size=18)
        self.thrust_unit = ft.Text('N', size=18)
        self.content = SimpleCard(
            "Thrust",
            ft.Row(
                tight=True,
                controls=[self.thrust_value, self.thrust_unit]
            )
        )

    def set_value(self, value: float):
        thrust = UnitParser.parse_thrust(value)
        self.thrust_value.value = thrust[0]
        self.thrust_unit.value = thrust[1]
        self.content.update()
