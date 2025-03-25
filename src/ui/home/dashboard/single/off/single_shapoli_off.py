import flet as ft

from ui.home.dashboard.single.off.thrust_power import ThrustPower
from ui.home.dashboard.single.single_power_chart import SinglePowerChart
from ui.home.dashboard.single.off.single_power_speed_torque import SinglePowerSpeedTorque


class SingleShaPoLiOff(ft.Stack):
    def __init__(self):
        super().__init__()

    def __create_top(self):
        self.top = SinglePowerSpeedTorque()

    def __create_bottom(self):
        self.bottom = ft.Container(
            content=SinglePowerChart(),
            expand=True
        )

    def build(self):
        self.__create_top()
        self.__create_bottom()

        thrust_power = ThrustPower()

        main_content = ft.Column(
            spacing=20,
            controls=[self.top, self.bottom]
        )

        self.controls = [main_content, thrust_power]
