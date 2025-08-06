import logging
import flet as ft

from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser
from common.global_data import gdata
from db.models.preference import Preference


class DualInstantPower(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

        self.font_size_of_label = 14
        self.font_size_of_value = 16
        self.font_size_of_unit = 12

        # 默认标准单位0-SI
        self.unit = 0
        try:
            preference: Preference = Preference.get()
            self.unit = preference.system_unit
        except:
            pass

    def build(self):
        try:
            if self.page is None or self.page.session is None:
                return

            self.__create_power_sps()
            self.__create_power_sps2()
            self.__create_power_total()

            controls = []

            if self.power_total:
                controls.append(self.power_total)

            if self.power_sps:
                controls.append(self.power_sps)

            if self.power_sps2:
                controls.append(self.power_sps2)

            if len(controls) > 0:
                content = ft.Column(
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    alignment=ft.MainAxisAlignment.END,
                    spacing=0,
                    controls=controls
                )
                self.content = SimpleCard(title=self.page.session.get("lang.common.power"), body=content)

        except:
            logging.exception('exception occured at DualInstantPower.build')

    def reload(self):
        try:
            power_sps = UnitParser.parse_power(gdata.configSPS.power, self.unit)
            power_sps2 = UnitParser.parse_power(gdata.configSPS2.power, self.unit)
            power_total = UnitParser.parse_power(
                gdata.configSPS.power + gdata.configSPS2.power,
                self.unit
            )

            self.power_sps_value.value = power_sps[0]
            self.power_sps_unit.value = power_sps[1]

            self.power_sps2_value.value = power_sps2[0]
            self.power_sps2_unit.value = power_sps2[1]

            self.power_total_value.value = power_total[0]
            self.power_total_unit.value = power_total[1]

            if self.content and self.content.page:
                self.content.update()

        except:
            logging.exception('exception occured at DualInstantGrid.reload')

    def __create_power_sps(self):
        try:
            if self.page is None or self.page.session is None:
                return

            self.sps_label = ft.Text(
                value=self.page.session.get("lang.common.sps"),
                text_align=ft.TextAlign.RIGHT,
                size=self.font_size_of_label,
                weight=ft.FontWeight.W_600
            )
            self.power_sps_value = ft.Text(
                value='0',
                size=self.font_size_of_value,
                width=80,
                text_align=ft.TextAlign.RIGHT,
                weight=ft.FontWeight.W_500
            )
            self.power_sps_unit = ft.Text(
                value='W',
                width=40,
                text_align=ft.TextAlign.LEFT,
                size=self.font_size_of_unit,
                weight=ft.FontWeight.W_500
            )

            self.power_sps = ft.Row(
                tight=True,
                controls=[
                    self.sps_label,
                    self.power_sps_value,
                    self.power_sps_unit
                ])
        except:
            logging.exception('exception occured at DualInstantGrid.__create_power_sps')

    def __create_power_sps2(self):
        try:
            if self.page is None or self.page.session is None:
                return

            self.sps2_label = ft.Text(
                value=self.page.session.get("lang.common.sps2"),
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
            self.power_sps2_unit = ft.Text(
                value='W',
                width=40,
                text_align=ft.TextAlign.LEFT,
                size=self.font_size_of_unit,
                weight=ft.FontWeight.W_500
            )
            self.power_sps2 = ft.Row(
                tight=True,
                controls=[
                    self.sps2_label,
                    self.power_sps2_value,
                    self.power_sps2_unit
                ])

        except:
            logging.exception('exception occured at DualInstantGrid.__create_power_sps2')

    def __create_power_total(self):
        try:
            if self.page is None or self.page.session is None:
                return

            self.total_label = ft.Text(
                value=self.page.session.get("lang.common.total"),
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
            self.power_total_unit = ft.Text(
                value='W', width=40,
                text_align=ft.TextAlign.LEFT,
                size=self.font_size_of_unit,
                weight=ft.FontWeight.W_500
            )
            self.power_total = ft.Row(
                tight=True,
                controls=[
                    self.total_label,
                    self.power_total_value,
                    self.power_total_unit
                ])
        except:
            logging.exception('exception occured at DualInstantGrid.__create_power_total')
