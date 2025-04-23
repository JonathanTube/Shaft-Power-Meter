import flet as ft
from ui.common.meter_half import MeterHalf
from db.models.system_settings import SystemSettings
from common.global_data import gdata
from db.models.propeller_setting import PropellerSetting


class EEXILimitedPower(ft.Container):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.expand = True

        self.container_width = width
        self.container_height = height

        propeller_settings: PropellerSetting = PropellerSetting.get()
        self.system_settings: SystemSettings = SystemSettings.get()

        self.unlimited_power = propeller_settings.shaft_power_of_mcr_operating_point
        self.eexi_power = self.system_settings.eexi_limited_power
        self.normal_power = self.eexi_power * 0.9

    def build(self):
        meter_radius = self.container_width * 0.4
        green = self.normal_power
        orange = self.eexi_power - self.normal_power
        red = self.unlimited_power - self.eexi_power
        self.meter_half = MeterHalf(radius=meter_radius, green=green, orange=orange, red=red)
        self.title = ft.Text(f"{self.page.session.get('lang.common.eexi_limited_power')}(%)", size=16, weight=ft.FontWeight.W_600)
        self.unlimited_mode = ft.Text(f"{self.page.session.get('lang.common.power_unlimited_mode')}:", weight=ft.FontWeight.W_400)
        self.unlimited_mode_icon = ft.Icon(ft.icons.INFO_OUTLINED, color=ft.Colors.GREEN, size=18)

        self.unlimited_mode_row = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            visible=False,
            controls=[self.unlimited_mode, self.unlimited_mode_icon]
        )

        row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[self.title, self.unlimited_mode_row])

        self.content = ft.Container(
            border=ft.border.all(
                width=0.5,
                color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE)
            ),
            border_radius=10,
            padding=ft.padding.all(10),
            content=ft.Column(
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[row, self.meter_half]
            )
        )

    def reload(self):
        active_value = gdata.sps1_power + gdata.sps2_power
        inactive_value = self.unlimited_power - active_value
        self.meter_half.set_outer_value(active_value, inactive_value)
        self.update_mode()

    def update_mode(self):
        instant_power = gdata.sps1_power + gdata.sps2_power
        if instant_power <= self.normal_power:
            self.unlimited_mode_icon.visible = False
        elif instant_power <= self.eexi_power:
            self.unlimited_mode_icon.color = ft.Colors.ORANGE
            self.unlimited_mode.color = ft.Colors.ORANGE
            self.unlimited_mode_icon.visible = True
        else:
            self.unlimited_mode_icon.color = ft.Colors.RED
            self.unlimited_mode.color = ft.Colors.RED
            self.unlimited_mode_icon.visible = True

        self.unlimited_mode_icon.update()
        self.unlimited_mode.update()
