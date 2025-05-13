import flet as ft
from ui.home.dashboard.meters.speed_meter import SpeedMeter
from ui.home.dashboard.meters.power_meter import PowerMeter
from ui.home.dashboard.meters.torque_meter import TorqueMeter
from ui.common.simple_card import SimpleCard


class SingleMeters(ft.Container):
    def __init__(self):
        super().__init__()

    def build(self):
        self.speed_meter = SpeedMeter("sps1")
        self.power_meter = PowerMeter("sps1")
        self.torque_meter = TorqueMeter("sps1")

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

    def reload(self):
        self.speed_meter.reload()
        self.power_meter.reload()
        self.torque_meter.reload()
