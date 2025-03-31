import flet as ft
from ui.home.dashboard.meters.speed_meter import SpeedMeter
from ui.home.dashboard.meters.power_meter import PowerMeter
from ui.home.dashboard.meters.torque_meter import TorqueMeter
from ui.common.simple_card import SimpleCard


class SingleMeters(ft.Container):
    def __init__(self):
        super().__init__()

    def build(self):
        self.speed_meter = SpeedMeter()

        self.power_meter = PowerMeter()

        self.torque_meter = TorqueMeter()

        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            controls=[
                SimpleCard(
                    body=self.speed_meter,
                    body_bottom_right=False,
                    expand=False
                ),
                SimpleCard(
                    body=self.power_meter,
                    body_bottom_right=False,
                    expand=False
                ),
                SimpleCard(
                    body=self.torque_meter,
                    body_bottom_right=False,
                    expand=False
                )

            ]
        )

    def set_power_limit(self, power_max: float, power_warning: float, unit: int):
        self.power_meter.set_limit(power_max, power_warning, unit)

    def set_torque_limit(self, torque_max: float, torque_warning: float, unit: int):
        self.torque_meter.set_limit(torque_max, torque_warning, unit)

    def set_speed_limit(self, speed_max: float, speed_warning: float):
        self.speed_meter.set_limit(speed_max, speed_warning)

    def set_data(self, speed: float, power: float, torque: float, unit: int):
        self.speed_meter.set_data(speed)
        self.power_meter.set_data(power, unit)
        self.torque_meter.set_data(torque, unit)