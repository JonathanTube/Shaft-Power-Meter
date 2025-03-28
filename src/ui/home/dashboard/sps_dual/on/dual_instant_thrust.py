import flet as ft

from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser


class DualInstantThrust(ft.Container):
    def __init__(self, visible: bool = True):
        super().__init__()
        self.expand = True
        self.visible = visible

        self.font_size_of_label = 14
        self.font_size_of_value = 16
        self.font_size_of_unit = 12

    def build(self):
        self.__create_thrust_sps1()
        self.__create_thrust_sps2()

        content = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.END,
            alignment=ft.MainAxisAlignment.END,
            controls=[self.thrust_sps1, self.thrust_sps2]
        )

        self.content = SimpleCard(title="Thrust", body=content)

    def set_data(self, thrust_sps1_value: float, thrust_sps2_value: float):
        thrust_sps1 = UnitParser.parse_thrust(thrust_sps1_value)
        thrust_sps2 = UnitParser.parse_thrust(thrust_sps2_value)

        self.thrust_sps1_value.value = thrust_sps1[0]
        self.thrust_sps1_unit.value = thrust_sps1[1]

        self.thrust_sps2_value.value = thrust_sps2[0]
        self.thrust_sps2_unit.value = thrust_sps2[1]

        self.content.update()

    def __create_thrust_sps1(self):
        self.sps1_label = ft.Text(
            value='SP1',
            text_align=ft.TextAlign.RIGHT,
            size=self.font_size_of_label,
            weight=ft.FontWeight.W_600
        )
        self.thrust_sps1_value = ft.Text(
            value='0',
            size=self.font_size_of_value,
            width=80,
            text_align=ft.TextAlign.RIGHT,
            weight=ft.FontWeight.W_500
        )
        self.thrust_sps1_unit = ft.Text('kN', width=30,
                                        text_align=ft.TextAlign.LEFT,
                                        size=self.font_size_of_unit,
                                        weight=ft.FontWeight.W_500
                                        )

        self.thrust_sps1 = ft.Row(
            tight=True,
            controls=[
                self.sps1_label,
                self.thrust_sps1_value,
                self.thrust_sps1_unit
            ])

    def __create_thrust_sps2(self):
        self.sps2_label = ft.Text(
            value='SP2',
            text_align=ft.TextAlign.END,
            size=self.font_size_of_label,
            weight=ft.FontWeight.W_600
        )
        self.thrust_sps2_value = ft.Text(
            value='0',
            size=self.font_size_of_value,
            width=80,
            text_align=ft.TextAlign.END,
            weight=ft.FontWeight.W_500
        )
        self.thrust_sps2_unit = ft.Text('kN', width=30,
                                        text_align=ft.TextAlign.LEFT,
                                        size=self.font_size_of_unit,
                                        weight=ft.FontWeight.W_500
                                        )
        self.thrust_sps2 = ft.Row(
            tight=True,
            controls=[
                self.sps2_label,
                self.thrust_sps2_value,
                self.thrust_sps2_unit
            ])

    def did_mount(self):
        self.set_language()

    def before_update(self):
        self.set_language()

    def set_language(self):
        self.sps1_label.value = self.page.session.get("lang.common.sps1")
        self.sps2_label.value = self.page.session.get("lang.common.sps2")
        self.content.set_title(self.page.session.get("lang.common.thrust"))
