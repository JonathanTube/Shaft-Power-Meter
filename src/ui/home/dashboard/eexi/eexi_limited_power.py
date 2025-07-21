import logging
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
        system_settings: SystemSettings = SystemSettings.get()

        self.unlimited_power = propeller_settings.shaft_power_of_mcr_operating_point
        self.amount_of_propeller = system_settings.amount_of_propeller
        self.eexi_power = system_settings.eexi_limited_power
        self.normal_power = self.eexi_power * 0.9

    def build(self):
        try:
            if self.page is None or self.page.window is None or self.page.session is None:
                return

            if self.page.window.height <= 600:
                meter_radius = self.container_height * 0.6
            else:
                meter_radius = self.container_height * 0.56
            green = self.normal_power
            orange = self.eexi_power - self.normal_power
            red = self.unlimited_power - self.eexi_power
            self.meter_half = MeterHalf(radius=meter_radius, green=green, orange=orange, red=red)
            self.title = ft.Text(f"{self.page.session.get('lang.common.eexi_limited_power')}(%)", size=16, weight=ft.FontWeight.W_600)
            self.unlimited_mode = ft.Text(f"{self.page.session.get('lang.common.power_unlimited_mode')}", weight=ft.FontWeight.W_400)
            self.unlimited_mode_icon = ft.Icon(ft.Icons.INFO_OUTLINED, color=ft.Colors.GREEN, size=18)

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
        except:
            logging.exception('exception occured at EEXILimitedPower.reload')



    def reload(self):
        try:
            if self.page:
                active_value = gdata.sps_power

                if self.amount_of_propeller == 2:
                    active_value += gdata.sps2_power

                inactive_value = self.unlimited_power - active_value

                if self.meter_half is not None:
                    self.meter_half.set_outer_value(active_value, inactive_value)
                    if self.eexi_power > 0:
                        percentage_of_eexi = int(active_value / self.eexi_power * 100)
                        self.meter_half.set_center_value(percentage_of_eexi)

                self.update_mode()
        except:
            logging.exception('exception occured at EEXILimitedPower.reload')

    def update_mode(self):
        try:
            if self.page:
                instant_power = gdata.sps_power
                if self.amount_of_propeller == 2:
                    instant_power += gdata.sps2_power

                self.unlimited_mode_row.visible = instant_power > self.normal_power

                if instant_power <= self.eexi_power:
                    self.unlimited_mode_icon.color = ft.Colors.ORANGE
                    self.unlimited_mode.color = ft.Colors.ORANGE
                else:
                    self.unlimited_mode_icon.color = ft.Colors.RED
                    self.unlimited_mode.color = ft.Colors.RED
                
                if self.unlimited_mode_row and self.unlimited_mode_row.page:
                    self.unlimited_mode_row.update()
        except:
            logging.exception('exception occured at EEXILimitedPower.update_mode')
