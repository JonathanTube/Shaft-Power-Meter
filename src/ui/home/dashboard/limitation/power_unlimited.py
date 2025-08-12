import logging
import flet as ft
from utils.unit_parser import UnitParser
from db.models.preference import Preference
from common.global_data import gdata


class PowerUnlimited(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

        self.is_dual = gdata.configCommon.amount_of_propeller == 2
        self.power = gdata.configCommon.unlimited_power

        preference: Preference = Preference.get()
        self.system_unit = preference.system_unit

    def build(self):
        try:
            if self.page is None or self.page.session is None:
                return

            self.title = ft.Text(self.page.session.get("lang.common.unlimited_power"), weight=ft.FontWeight.W_600)
            power = self.power * 2 if self.is_dual else self.power
            power_and_unit = UnitParser.parse_power(power, self.system_unit)
            self.unlimited_power_value = ft.Text(power_and_unit[0])
            self.unlimited_power_unit = ft.Text(power_and_unit[1])

            self.content = ft.Container(
                border=ft.border.all(
                    width=0.5,
                    color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE)
                ),
                border_radius=10,
                padding=ft.padding.all(10),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        self.title,
                        ft.Row(controls=[
                            self.unlimited_power_value,
                            self.unlimited_power_unit
                        ])
                    ]
                ))
        except:
            logging.exception('exception occured at PowerUnlimited.build')
