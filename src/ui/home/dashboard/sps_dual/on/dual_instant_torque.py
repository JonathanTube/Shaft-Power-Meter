import logging
import flet as ft

from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser
from common.global_data import gdata


class DualInstantTorque(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        # self.bgcolor = ft.Colors.PURPLE_400

        self.font_size_of_label = 14
        self.font_size_of_value = 16
        self.font_size_of_unit = 12

    def build(self):
        try:
            if self.page is None or self.page.session is None:
                return

            self.__create_torque_sps()
            self.__create_torque_sps2()

            controls = []
            if self.torque_sps:
                controls.append(self.torque_sps)

            if self.torque_sps2:
                controls.append(self.torque_sps2)

            if len(controls) > 0:
                content = ft.Column(
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    alignment=ft.MainAxisAlignment.END,
                    spacing=0,
                    controls=controls
                )

                self.content = SimpleCard(title=self.page.session.get("lang.common.torque"), body=content)
        except:
            logging.exception('exception occured at DualInstantTorque.build')

    def reload(self):
        try:
            unit = gdata.configPreference.system_unit
            torque_sps = UnitParser.parse_torque(gdata.configSPS.torque, unit)
            torque_sps2 = UnitParser.parse_torque(gdata.configSPS2.torque, unit)

            self.torque_sps_value.value = torque_sps[0]
            self.torque_sps_unit.value = torque_sps[1]

            self.torque_sps2_value.value = torque_sps2[0]
            self.torque_sps2_unit.value = torque_sps2[1]

            if self.content and self.content.page:
                self.content.update()
        except:
            logging.exception('exception occured at DualInstantTorque.reload')

    def __create_torque_sps(self):
        try:
            if self.page is None or self.page.session is None:
                return

            self.sps_label = ft.Text(
                value=self.page.session.get("lang.common.sps"),
                text_align=ft.TextAlign.RIGHT,
                size=self.font_size_of_label,
                weight=ft.FontWeight.W_600
            )
            self.torque_sps_value = ft.Text(
                value='0',
                size=self.font_size_of_value,
                width=80,
                text_align=ft.TextAlign.RIGHT,
                weight=ft.FontWeight.W_500
            )
            self.torque_sps_unit = ft.Text(
                value='kNm',
                width=40,
                text_align=ft.TextAlign.LEFT,
                size=self.font_size_of_unit,
                weight=ft.FontWeight.W_500
            )
            self.torque_sps = ft.Row(
                tight=True,
                controls=[
                    self.sps_label,
                    self.torque_sps_value,
                    self.torque_sps_unit
                ])
        except:
            logging.exception('exception occured at DualInstantTorque.__create_torque_sps')

    def __create_torque_sps2(self):
        try:
            if self.page is None or self.page.session is None:
                return

            self.sps2_label = ft.Text(
                value=self.page.session.get("lang.common.sps2"),
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
            self.torque_sps2_unit = ft.Text(
                value='kNm',
                width=40,
                text_align=ft.TextAlign.LEFT,
                size=self.font_size_of_unit,
                weight=ft.FontWeight.W_500
            )
            self.torque_sps2 = ft.Row(
                tight=True,
                controls=[
                    self.sps2_label,
                    self.torque_sps2_value,
                    self.torque_sps2_unit
                ])
        except:
            logging.exception('exception occured at DualInstantTorque.__create_torque_sps2')
