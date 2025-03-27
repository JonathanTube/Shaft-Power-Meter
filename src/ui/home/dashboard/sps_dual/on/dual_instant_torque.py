import flet as ft

from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser


class DualInstantTorque(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        # self.bgcolor = ft.colors.PURPLE_400

        self.font_size_of_label = 14
        self.font_size_of_value = 16
        self.font_size_of_unit = 12

    def build(self):
        self.__create_torque_sps1()
        self.__create_torque_sps2()

        content = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.END,
            alignment=ft.MainAxisAlignment.END,
            controls=[
                self.torque_sps1,
                self.torque_sps2
            ]
        )

        self.content = SimpleCard(title="Torque", body=content)

    def set_data(self, torque_sps1_value: str, torque_sps2_value: str):
        torque_sps1 = UnitParser.parse_torque(torque_sps1_value)
        torque_sps2 = UnitParser.parse_torque(torque_sps2_value)

        self.torque_sps1_value.value = torque_sps1[0]
        self.torque_sps1_unit.value = torque_sps1[1]

        self.torque_sps2_value.value = torque_sps2[0]
        self.torque_sps2_unit.value = torque_sps2[1]

        self.content.update()

    def __create_torque_sps1(self):
        label = ft.Text(
            value='SPS1:',
            width=40,   
            text_align=ft.TextAlign.RIGHT,
            size=self.font_size_of_label,
            weight=ft.FontWeight.W_600
        )
        self.torque_sps1_value = ft.Text(
            value='0',
            size=self.font_size_of_value,
            width=80,
            text_align=ft.TextAlign.RIGHT,
            weight=ft.FontWeight.W_500
        )
        self.torque_sps1_unit = ft.Text('Nm', width=30,
                                        text_align=ft.TextAlign.LEFT,
                                        size=self.font_size_of_unit,
                                        weight=ft.FontWeight.W_500
                                        )
        self.torque_sps1 = ft.Row(
            tight=True,
            controls=[
                label,
                self.torque_sps1_value,
                self.torque_sps1_unit
            ])

    def __create_torque_sps2(self):
        label = ft.Text(
            value='SPS2:',
            width=40,
            text_align=ft.TextAlign.END,
            size=self.font_size_of_label,
            weight=ft.FontWeight.W_600
        )
        self.torque_sps2_value = ft.Text(
            value='0',
            size=self.font_size_of_value,
            width=80,
            text_align=ft.TextAlign.END,
            weight=ft.FontWeight.W_500
        )
        self.torque_sps2_unit = ft.Text('Nm', width=30,
                                        text_align=ft.TextAlign.LEFT,
                                        size=self.font_size_of_unit,
                                        weight=ft.FontWeight.W_500
                                        )
        self.torque_sps2 = ft.Row(
            tight=True,
            controls=[
                label,
                self.torque_sps2_value,
                self.torque_sps2_unit
            ])
