import flet as ft
import asyncio
from db.models.data_log import DataLog
from ui.home.dashboard.meters.speed_meter import SpeedMeter
from ui.home.dashboard.meters.power_meter import PowerMeter
from ui.home.dashboard.meters.torque_meter import TorqueMeter
from db.models.limitations import Limitations
from db.models.system_settings import SystemSettings
from ui.home.dashboard.thrust.thrust_power import ThrustPower


class DualMeters(ft.Container):
    def __init__(self, name: str = 'SPS1'):
        super().__init__()
        self.name = name

        self.speed_max = 0
        self.speed_warning = 0
        self.power_max = 0
        self.power_warning = 0
        self.torque_max = 0
        self.torque_warning = 0

        self.display_thrust = False

        self.padding = ft.padding.only(
            left=10, right=10, top=10, bottom=10
        )
        self.border_radius = ft.border_radius.all(10)
        self.shadow = ft.BoxShadow(
            spread_radius=2,
            blur_radius=4,
            color=ft.colors.with_opacity(0.15, ft.colors.INVERSE_SURFACE),
            offset=ft.Offset(0, 1),
            blur_style=ft.ShadowBlurStyle.OUTER
        )

        self.__load_settings()

    def did_mount(self):
        self._task = self.page.run_task(self.__load_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    def __load_settings(self):
        limitations = Limitations.get_or_none()

        if limitations:
            self.speed_max = limitations.speed_max
            self.speed_warning = limitations.speed_warning

            self.power_max = limitations.power_max
            self.power_warning = limitations.power_warning

            self.torque_max = limitations.torque_max
            self.torque_warning = limitations.torque_warning

        system_settings = SystemSettings.get_or_none()
        if system_settings:
            self.display_thrust = system_settings.display_thrust

    async def __load_data(self):
        while True:
            data_log = DataLog.select(
                DataLog.revolution,
                DataLog.power,
                DataLog.torque,
                DataLog.thrust
            ).where(
                DataLog.name == self.name
            ).order_by(DataLog.id.desc()).first()
            if data_log:
                self.speed_meter.set_data(data_log.revolution)
                self.power_meter.set_data(data_log.power)
                self.torque_meter.set_data(data_log.torque)
                self.thrust_power.set_data(data_log.thrust)

            await asyncio.sleep(1)

    def build(self):
        width = self.page.window.width * 0.45
        height = self.page.window.height * 0.4
        self.speed_meter = SpeedMeter(
            self.speed_max, self.speed_warning, radius=70)
        self.power_meter = PowerMeter(
            self.power_max, self.power_warning, radius=100)
        self.torque_meter = TorqueMeter(
            self.torque_max, self.torque_warning, radius=70)

        self.thrust_power = ThrustPower()

        self.content = ft.Stack(
            width=width,
            height=height,
            alignment=ft.alignment.center,
            controls=[
                ft.Text(
                    value=self.name,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    left=0,
                    top=0
                ),
                ft.Container(
                    content=self.speed_meter,
                    bottom=0,
                    left=0
                ),
                ft.Container(
                    content=self.power_meter
                ),
                ft.Container(
                    content=self.torque_meter,
                    bottom=0,
                    right=0
                ),
                self.thrust_power
            ])
