import flet as ft
from utils.unit_parser import UnitParser
from db.models.preference import Preference
from db.models.propeller_setting import PropellerSetting


class PowerUnlimited(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        preference: Preference = Preference.get()
        self.system_unit = preference.system_unit

        propeller_settings: PropellerSetting = PropellerSetting.get()
        self.power = propeller_settings.shaft_power_of_mcr_operating_point

    def build(self):
        self.title = ft.Text(self.page.session.get("lang.common.unlimited_power"), weight=ft.FontWeight.W_600)
        power_and_unit = UnitParser.parse_power(self.power, self.system_unit)
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
