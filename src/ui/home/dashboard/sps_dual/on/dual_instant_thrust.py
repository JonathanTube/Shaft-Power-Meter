import logging
import flet as ft

from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser
from db.models.system_settings import SystemSettings
from common.global_data import gdata
from db.models.preference import Preference
from common.global_data import gdata


class DualInstantThrust(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

        self.font_size_of_label = 14
        self.font_size_of_value = 16
        self.font_size_of_unit = 12

        self.visible = gdata.configCommon.show_thrust

        self.unit = 0

    def build(self):
        try:
            preference: Preference = Preference.get()
            self.unit = preference.system_unit

            if self.page is None or self.page.session is None:
                return

            self.__create_thrust_sps()
            self.__create_thrust_sps2()

            controls = []
            if self.thrust_sps:
                controls.append(self.thrust_sps)

            if self.thrust_sps2:
                controls.append(self.thrust_sps2)

            if len(controls) > 0:
                content = ft.Column(
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.END,
                    alignment=ft.MainAxisAlignment.END,
                    spacing=0,
                    controls=controls
                )

                self.content = SimpleCard(title=self.page.session.get("lang.common.thrust"), body=content)
        except:
            logging.exception('exception occured at DualInstantThrust.build')

    def reload(self):
        try:
            thrust_sps = UnitParser.parse_thrust(gdata.configSPS.thrust, self.unit)
            thrust_sps2 = UnitParser.parse_thrust(gdata.configSPS2.thrust, self.unit)

            self.thrust_sps_value.value = thrust_sps[0]
            self.thrust_sps_unit.value = thrust_sps[1]

            self.thrust_sps2_value.value = thrust_sps2[0]
            self.thrust_sps2_unit.value = thrust_sps2[1]

            if self.content and self.content.page:
                self.content.update()
        except:
            logging.exception('exception occured at DualInstantThrust.reload')

    def __create_thrust_sps(self):
        try:
            if self.page is None or self.page.session is None:
                return

            self.sps_label = ft.Text(
                value=self.page.session.get("lang.common.sps"),
                text_align=ft.TextAlign.RIGHT,
                size=self.font_size_of_label,
                weight=ft.FontWeight.W_600
            )
            self.thrust_sps_value = ft.Text(
                value='0',
                size=self.font_size_of_value,
                width=80,
                text_align=ft.TextAlign.RIGHT,
                weight=ft.FontWeight.W_500
            )
            self.thrust_sps_unit = ft.Text(
                value='kN',
                width=40,
                text_align=ft.TextAlign.LEFT,
                size=self.font_size_of_unit,
                weight=ft.FontWeight.W_500
            )
            self.thrust_sps = ft.Row(
                tight=True,
                controls=[
                    self.sps_label,
                    self.thrust_sps_value,
                    self.thrust_sps_unit
                ])
        except:
            logging.exception('exception occured at DualInstantThrust.__create_thrust_sps')

    def __create_thrust_sps2(self):
        try:
            if self.page is None or self.page.session is None:
                return

            self.sps2_label = ft.Text(
                value=self.page.session.get("lang.common.sps2"),
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
            self.thrust_sps2_unit = ft.Text(
                value='kN',
                width=40,
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
        except:
            logging.exception('exception occured at DualInstantThrust.__create_thrust_sps2')
