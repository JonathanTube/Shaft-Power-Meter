import flet as ft
from ui.home.dashboard.meters.speed_meter import SpeedMeter
from ui.home.dashboard.meters.power_meter import PowerMeter
from ui.home.dashboard.meters.torque_meter import TorqueMeter


class SingleMeters(ft.Row):
    def __init__(self, power_max: float, power_warning: float, speed_max: float, speed_warning: float, torque_max: float, torque_warning: float):
        super().__init__()

        self.alignment = ft.MainAxisAlignment.CENTER
        self.spacing = 20

        self.power_max = power_max
        self.power_warning = power_warning
        self.speed_max = speed_max
        self.speed_warning = speed_warning
        self.torque_max = torque_max
        self.torque_warning = torque_warning

    def build(self):
        self.speed_meter = SpeedMeter(self.speed_max, self.speed_warning)

        self.power_meter = PowerMeter(self.power_max, self.power_warning)

        self.torque_meter = TorqueMeter(self.torque_max, self.torque_warning)

        self.controls = [
            self.__create_container(self.speed_meter),
            self.__create_container(self.power_meter),
            self.__create_container(self.torque_meter)
        ]

    def set_data(self, speed: float, power: float, torque: float):
        self.speed_meter.set_data(speed)
        self.power_meter.set_data(power)
        self.torque_meter.set_data(torque)

    def __create_container(self, content: ft.Control):
        return ft.Container(
            content=content,
            padding=ft.padding.all(10),
            border_radius=ft.border_radius.all(10),
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=4,
                color=ft.colors.with_opacity(0.15, ft.colors.INVERSE_SURFACE),
                offset=ft.Offset(0, 1),
                blur_style=ft.ShadowBlurStyle.OUTER
            )
        )
