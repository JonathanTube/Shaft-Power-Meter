import flet as ft
from ui.home.dashboard.meters.speed_meter import SpeedMeter
from ui.home.dashboard.meters.power_meter import PowerMeter
from ui.home.dashboard.meters.torque_meter import TorqueMeter
from ui.common.simple_card import SimpleCard
from db.models.limitations import Limitations


class SingleMeters(ft.Container):
    def __init__(self):
        super().__init__()

    def build(self):
        limitations: Limitations = Limitations.get()
        self.speed_meter = SpeedMeter()
        self.speed_meter.set_limit(limitations.speed_max, limitations.speed_warning)
        self.power_meter = PowerMeter()
        self.power_meter.set_limit(limitations.power_max, limitations.power_warning)
        self.torque_meter = TorqueMeter()
        self.torque_meter.set_limit(limitations.torque_max, limitations.torque_warning)

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
        self.speed_meter.set_data()
        self.power_meter.set_data()
        self.torque_meter.set_data()
