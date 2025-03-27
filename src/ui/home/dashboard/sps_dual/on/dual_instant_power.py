import flet as ft

from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser


class DualInstantPower(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

        self.font_size_of_label = 14
        self.font_size_of_value = 16
        self.font_size_of_unit = 12

    def build(self):
        self.__create_power_sps1()
        self.__create_power_sps2()
        self.__create_power_total()

        content = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.END,
            alignment=ft.MainAxisAlignment.END,
            controls=[
                self.power_total,
                self.power_sps1,
                self.power_sps2
            ]
        )
        self.content = SimpleCard(title="Power", body=content)

    def set_data(self, power_sps1_value: float, power_sps2_value: float):
        power_sps1 = UnitParser.parse_power(power_sps1_value)
        power_sps2 = UnitParser.parse_power(power_sps2_value)
        power_total = UnitParser.parse_power(
            power_sps1_value + power_sps2_value)

        self.power_sps1_value.value = power_sps1[0]
        self.power_sps1_unit.value = power_sps1[1]

        self.power_sps2_value.value = power_sps2[0]
        self.power_sps2_unit.value = power_sps2[1]

        self.power_total_value.value = power_total[0]
        self.power_total_unit.value = power_total[1]

        self.content.update()

    def __create_power_sps1(self):
        label = ft.Text(
            value='SPS1:',
            width=40,
            text_align=ft.TextAlign.RIGHT,
            size=self.font_size_of_label,
            weight=ft.FontWeight.W_600
        )
        self.power_sps1_value = ft.Text(
            value='0',
            size=self.font_size_of_value,
            width=80,
            text_align=ft.TextAlign.RIGHT,
            weight=ft.FontWeight.W_500
        )
        self.power_sps1_unit = ft.Text('W', width=30,
                                       text_align=ft.TextAlign.LEFT,
                                       size=self.font_size_of_unit,
                                       weight=ft.FontWeight.W_500
                                       )

        self.power_sps1 = ft.Row(
            tight=True,
            controls=[
                label,
                self.power_sps1_value,
                self.power_sps1_unit
            ])

    def __create_power_sps2(self):
        label = ft.Text(
            value='SPS2:',
            width=40,
            text_align=ft.TextAlign.END,
            size=self.font_size_of_label,
            weight=ft.FontWeight.W_600
        )
        self.power_sps2_value = ft.Text(
            value='0',
            size=self.font_size_of_value,
            width=80,
            text_align=ft.TextAlign.END,
            weight=ft.FontWeight.W_500
        )
        self.power_sps2_unit = ft.Text('W', width=30,
                                       text_align=ft.TextAlign.LEFT,
                                       size=self.font_size_of_unit,
                                       weight=ft.FontWeight.W_500
                                       )
        self.power_sps2 = ft.Row(
            tight=True,
            controls=[
                label,
                self.power_sps2_value,
                self.power_sps2_unit
            ])

    def __create_power_total(self):
        label = ft.Text(
            value='Total:',
            width=40,
            text_align=ft.TextAlign.END,
            size=self.font_size_of_label,
            weight=ft.FontWeight.W_600
        )
        self.power_total_value = ft.Text(
            value='0',
            size=self.font_size_of_value,
            width=80,
            text_align=ft.TextAlign.END,
            weight=ft.FontWeight.W_500
        )
        self.power_total_unit = ft.Text('W', width=30,
                                        text_align=ft.TextAlign.LEFT,
                                        size=self.font_size_of_unit,
                                        weight=ft.FontWeight.W_500
                                        )

        self.power_total = ft.Row(
            tight=True,
            controls=[
                label,
                self.power_total_value,
                self.power_total_unit
            ])
