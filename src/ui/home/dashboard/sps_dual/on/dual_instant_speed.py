import flet as ft

from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser


class DualInstantSpeed(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        # self.bgcolor = ft.colors.BLUE_400

        self.font_size_of_label = 14
        self.font_size_of_value = 16
        self.font_size_of_unit = 12

    def build(self):
        self.__create_speed_sps1()
        self.__create_speed_sps2()

        content = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.END,
            alignment=ft.MainAxisAlignment.END,
            controls=[self.speed_sps1, self.speed_sps2]
        )

        self.content = SimpleCard(title=self.page.session.get("lang.common.speed"), body=content)

    def set_data(self, speed_sps1_value: int, speed_sps2_value: int):
        speed_sps1 = UnitParser.parse_speed(speed_sps1_value)
        speed_sps2 = UnitParser.parse_speed(speed_sps2_value)

        self.speed_sps1_value.value = speed_sps1[0]
        self.speed_sps1_unit.value = speed_sps1[1]

        self.speed_sps2_value.value = speed_sps2[0]
        self.speed_sps2_unit.value = speed_sps2[1]

        self.content.update()

    def __create_speed_sps1(self):
        self.sps1_label = ft.Text(
            value=self.page.session.get("lang.common.sps1"),
            text_align=ft.TextAlign.RIGHT,
            size=self.font_size_of_label,
            weight=ft.FontWeight.W_600
        )
        self.speed_sps1_value = ft.Text(
            value='0',
            size=self.font_size_of_value,
            width=80,
            text_align=ft.TextAlign.RIGHT,
            weight=ft.FontWeight.W_500
        )
        self.speed_sps1_unit = ft.Text(self.page.session.get("lang.common.rpm"), width=40,
                                       text_align=ft.TextAlign.LEFT,
                                       size=self.font_size_of_unit,
                                       weight=ft.FontWeight.W_500
                                       )
        self.speed_sps1 = ft.Row(
            tight=True,
            controls=[
                self.sps1_label,
                self.speed_sps1_value,
                self.speed_sps1_unit
            ])

    def __create_speed_sps2(self):
        self.sps2_label = ft.Text(
            value=self.page.session.get("lang.common.sps2"),
            text_align=ft.TextAlign.END,
            size=self.font_size_of_label,
            weight=ft.FontWeight.W_600
        )
        self.speed_sps2_value = ft.Text(
            value='0',
            size=self.font_size_of_value,
            width=80,
            text_align=ft.TextAlign.END,
            weight=ft.FontWeight.W_500
        )
        self.speed_sps2_unit = ft.Text(self.page.session.get("lang.common.rpm"), width=40,
                                       text_align=ft.TextAlign.LEFT,
                                       size=self.font_size_of_unit,
                                       weight=ft.FontWeight.W_500
                                       )
        self.speed_sps2 = ft.Row(
            tight=True,
            controls=[
                self.sps2_label,
                self.speed_sps2_value,
                self.speed_sps2_unit
            ]
        )