import flet as ft

from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser


class DualInstantThrust(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        # self.bgcolor = ft.colors.AMBER_400

        self.font_size_of_label = 14
        self.font_size_of_value = 16
        self.font_size_of_unit = 12

    def build(self):
        self.__create_thrust_sps1()
        self.__create_thrust_sps2()

        content = ft.Column(
            width=200,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.END,
            alignment=ft.MainAxisAlignment.END,
            controls=[self.thrust_sps1, self.thrust_sps2]
        )

        self.content = SimpleCard("Thrust", content)

    def set_data(self, thrust_sps1_value: float, thrust_sps2_value: float):
        thrust_sps1 = UnitParser.parse_thrust(thrust_sps1_value)
        thrust_sps2 = UnitParser.parse_thrust(thrust_sps2_value)

        self.thrust_sps1_value.value = thrust_sps1[0]
        self.thrust_sps1_unit.value = thrust_sps1[1]

        self.thrust_sps2_value.value = thrust_sps2[0]
        self.thrust_sps2_unit.value = thrust_sps2[1]

        self.content.update()

    def __create_thrust_sps1(self):
        self.thrust_sps1_value = ft.Text(
            value='0',
            size=self.font_size_of_value,
            weight=ft.FontWeight.W_500
        )
        self.thrust_sps1_unit = ft.Text('kN', size=self.font_size_of_unit)

        self.thrust_sps1 = ft.Row(
            tight=True,
            controls=[
                ft.Text(
                    value='SP1:',
                    size=self.font_size_of_label,
                    weight=ft.FontWeight.W_600
                ),
                self.thrust_sps1_value,
                self.thrust_sps1_unit
            ])

    def __create_thrust_sps2(self):
        self.thrust_sps2_value = ft.Text(
            value='0',
            size=self.font_size_of_value,
            weight=ft.FontWeight.W_500
        )
        self.thrust_sps2_unit = ft.Text('kN', size=self.font_size_of_unit)
        self.thrust_sps2 = ft.Row(
            tight=True,
            controls=[
                ft.Text(
                    value='SP2:',
                    size=self.font_size_of_label,
                    weight=ft.FontWeight.W_600
                ),
                self.thrust_sps2_value,
                self.thrust_sps2_unit
            ])
