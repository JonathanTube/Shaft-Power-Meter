import flet as ft

from ui.home.dashboard.single.off.thrust_power import ThrustPower
from ui.home.dashboard.single.power_chart import PowerChart
from ui.home.dashboard.single.off.power_speed_torque import PowerSpeedTorque
from ui.home.dashboard.single.on.eexi_limited_power import EEXILimitedPower
from ui.home.dashboard.single.on.instant_value_grid import InstantValueGrid


class SingleShaPoLiOff(ft.Stack):
    def __init__(self):
        super().__init__()

    def __create_top(self):
        self.top = PowerSpeedTorque()

    def __create_bottom(self):
        self.bottom = ft.Container(
            content=PowerChart(),
            expand=True
        )

    def build(self):
        self.__create_top()
        self.__create_bottom()

        thrust_power = ThrustPower()

        main_content = ft.Column(controls=[self.top, self.bottom])

        self.controls = [main_content, thrust_power]
