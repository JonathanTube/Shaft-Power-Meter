import flet as ft
import asyncio
from ui.common.meter_half import MeterHalf
from db.models.system_settings import SystemSettings
from db.models.propeller_setting import PropellerSetting
from db.models.data_log import DataLog


class EEXILimitedPower(ft.Card):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.container_width = width
        self.container_height = height

        self.limited_power_normal = 0
        self.limited_power_warning = 0
        self.unlimited_power = 0
        self._task = None

    def build(self):
        meter_radius = self.container_width * 0.46
        self.meter_half = MeterHalf(radius=meter_radius)
        column = ft.Column(
            expand=True,
            spacing=self.container_height * 0.1,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    'EEXI Limited Power(%)',
                    weight=ft.FontWeight.BOLD,
                    size=20
                ),
                self.meter_half
            ])

        container = ft.Container(
            content=column,
            alignment=ft.alignment.center,
            padding=10,
            width=self.container_width + 10,
            height=self.container_height
        )

        self.content = container

    def did_mount(self):
        self.__load_data()
        self.__set_meter_half_inner()
        self._task = asyncio.create_task(self.__set_meter_half_outer())

    def will_unmount(self):
        self._task.cancel()

    def __load_data(self):
        propeller_settings = PropellerSetting.get_or_none()
        if propeller_settings is None:
            return

        system_settings = SystemSettings.get_or_none()
        if system_settings is None:
            return

        self.limited_power_normal = system_settings.eexi_limited_power * 0.9
        self.limited_power_warning = system_settings.eexi_limited_power
        self.unlimited_power = propeller_settings.shaft_power_of_mcr_operating_point

    def __set_meter_half_inner(self):
        green = self.limited_power_normal
        print(f"green: {green}")
        orange = self.limited_power_warning - self.limited_power_normal
        print(f"orange: {orange}")
        red = self.unlimited_power - self.limited_power_warning
        print(f"red: {red}")
        self.meter_half.set_inner_value(green, orange, red)

    async def __set_meter_half_outer(self):
        while True:
            data_log = DataLog.select().order_by(DataLog.id.desc()).first()
            green = data_log.power
            grey = self.unlimited_power - data_log.power
            self.meter_half.set_outer_value(green, grey)
            await asyncio.sleep(1)
