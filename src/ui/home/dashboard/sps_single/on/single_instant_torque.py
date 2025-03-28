import flet as ft
from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser


class SingleInstantTorque(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def build(self):
        self.torque_value = ft.Text(
            '0', size=18, width=80, text_align=ft.TextAlign.RIGHT
        )

        self.torque_unit = ft.Text(
            'Nm', size=18, width=40, text_align=ft.TextAlign.LEFT
        )
        self.content = SimpleCard(
            title="Torque",
            body=ft.Row(
                tight=True,
                controls=[self.torque_value, self.torque_unit]
            )
        )

    def set_value(self, value: float):
        torque = UnitParser.parse_torque(value)
        self.torque_value.value = torque[0]
        self.torque_unit.value = torque[1]
        self.content.update()

    def set_language(self):
        session = self.page.session
        self.content.set_title(session.get("lang.common.torque"))

    def before_update(self):
        self.set_language()

    def did_mount(self):
        self.set_language()
