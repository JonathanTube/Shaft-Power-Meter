import logging
import flet as ft
from utils.unit_parser import UnitParser
from db.models.preference import Preference
from db.models.system_settings import SystemSettings


class PowerLimited(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        preference: Preference = Preference.get()
        self.system_unit = preference.system_unit

        system_settings: SystemSettings = SystemSettings.get()
        self.power = system_settings.eexi_limited_power

    def build(self):
        try:
            self.title = ft.Text(self.page.session.get("lang.common.limited_power"), weight=ft.FontWeight.W_600)

            power_and_unit = UnitParser.parse_power(self.power, self.system_unit)
            self.limited_power_value = ft.Text(power_and_unit[0])
            self.limited_power_unit = ft.Text(power_and_unit[1])

            self.content = ft.Container(
                padding=ft.padding.all(10),
                border=ft.border.all(
                    width=0.5,
                    color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE)
                ),
                border_radius=10,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        self.title,
                        ft.Row(controls=[
                            self.limited_power_value,
                            self.limited_power_unit
                        ])
                    ]
                ))

        except:
            logging.exception('exception occured at PowerLimited.build')

