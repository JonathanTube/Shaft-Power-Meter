import flet as ft

from ui.home.dashboard.meters.speed_meter import SpeedMeter
from ui.home.dashboard.meters.power_meter import PowerMeter
from ui.home.dashboard.meters.torque_meter import TorqueMeter
from ui.home.dashboard.thrust.thrust_power import ThrustPower
from ui.common.simple_card import SimpleCard
from typing import Literal


class DualMeters(ft.Container):
    def __init__(self, name: Literal["sps1", "sps2"]):
        super().__init__()
        self.expand = True
        self.name = name

    def build(self):
        width = self.page.window.width * 0.45
        height = self.page.window.height * 0.4

        self.speed_meter = SpeedMeter(self.name)
        self.power_meter = PowerMeter(self.name)
        self.torque_meter = TorqueMeter(self.name)
        self.thrust_meter = ThrustPower(self.name)

        title = self.page.session.get("lang.common.sps1")
        if self.name == "sps2":
            title = self.page.session.get("lang.common.sps2")

        self.content = ft.Stack(
            controls=[
                ft.Text(value=title, size=18, weight=ft.FontWeight.BOLD, left=10, top=10),
                self.thrust_meter,
                SimpleCard(
                    body_bottom_right=False,
                    body=ft.Stack(
                        width=width,
                        height=height,
                        alignment=ft.alignment.center,
                        controls=[
                            ft.Container(content=self.speed_meter, bottom=0, left=0),
                            ft.Container(content=self.power_meter, top=0),
                            ft.Container(content=self.torque_meter, bottom=0, right=0)
                        ])
                )
            ])

    def reload(self):
        self.power_meter.reload()
        self.torque_meter.reload()
        self.speed_meter.reload()
        self.thrust_meter.reload()
