import flet as ft
import asyncio
from ui.common.meter_half import MeterHalf
from db.models.system_settings import SystemSettings
from common.global_data import gdata


class EEXILimitedPower(ft.Container):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.expand = True

        self.container_width = width
        self.container_height = height

        self.unlimited_power = 0
        self._task = None

        self.system_settings = SystemSettings.get()
        self.eexi_limited_power = self.system_settings.eexi_limited_power

    def build(self):
        meter_radius = self.container_width * 0.4
        self.meter_half = MeterHalf(radius=meter_radius)
        self.title = ft.Text(
            f"{self.page.session.get('lang.common.eexi_limited_power')}(%)", size=16, weight=ft.FontWeight.W_600)
        self.unlimited_mode = ft.Text(
            f"{self.page.session.get('lang.common.power_unlimited_mode')}:", weight=ft.FontWeight.W_400)
        self.unlimited_mode_icon = ft.Icon(
            ft.icons.INFO_OUTLINED, color=ft.Colors.GREEN, size=18)

        self.unlimited_mode_row = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            visible=False,
            controls=[self.unlimited_mode, self.unlimited_mode_icon]
        )

        row = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                     controls=[self.title, self.unlimited_mode_row])

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

    def set_config(self, normal: float, warning: float, unlimited: float):
        self.unlimited_power = unlimited
        green = normal
        orange = warning - normal
        red = unlimited - warning
        self.meter_half.set_inner_value(green, orange, red)

    def set_value(self, power: float):
        active_value = power
        # print(f"unlimited_power: {self.unlimited_power}")
        inactive_value = self.unlimited_power - power
        # print(f"active_value: {active_value}, inactive_value: {inactive_value}")
        self.meter_half.set_outer_value(active_value, inactive_value)

    def did_mount(self):
        self._task = self.page.run_task(self.__update_mode)

    async def __update_mode(self):
        while True:
            sps1_instant_power = gdata.sps1_power
            sps2_instant_power = gdata.sps2_power
            instant_power = sps1_instant_power + sps2_instant_power

            # print(f"instant_power: {instant_power}")
            # print(f"eexi_limited_power: {self.eexi_limited_power}")

            if instant_power <= self.eexi_limited_power * 0.9:
                self.unlimited_mode_icon.visible = False
            elif instant_power <= self.eexi_limited_power:
                self.unlimited_mode_icon.color = ft.Colors.ORANGE
                self.unlimited_mode.color = ft.Colors.ORANGE
                self.unlimited_mode_icon.visible = True
            else:
                # print("power breach")
                self.unlimited_mode_icon.color = ft.Colors.RED
                self.unlimited_mode.color = ft.Colors.RED
                self.unlimited_mode_icon.visible = True

            self.unlimited_mode_icon.update()
            self.unlimited_mode.update()
            await asyncio.sleep(1)

    def will_unmount(self):
        if self._task:
            self._task.cancel()
            self._task = None
