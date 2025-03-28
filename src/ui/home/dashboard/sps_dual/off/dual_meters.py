import flet as ft

from ui.home.dashboard.meters.speed_meter import SpeedMeter
from ui.home.dashboard.meters.power_meter import PowerMeter
from ui.home.dashboard.meters.torque_meter import TorqueMeter
from ui.common.simple_card import SimpleCard
from ui.home.dashboard.thrust.thrust_power import ThrustPower


class DualMeters(ft.Container):
    def __init__(self, name: str = 'SPS1'):
        super().__init__()
        self.expand = True
        self.name = name

    def build(self):
        width = self.page.window.width * 0.45
        height = self.page.window.height * 0.4
        self.speed_meter = SpeedMeter(radius=75)
        self.power_meter = PowerMeter(radius=90)
        self.torque_meter = TorqueMeter(radius=75)
        self.thrust_meter = ThrustPower()

        self.title = ft.Text(
            value=self.name,
            size=18,
            weight=ft.FontWeight.BOLD,
            left=10,
            top=10
        )

        self.content = ft.Stack(
            controls=[
                self.title,
                self.thrust_meter,
                SimpleCard(
                    body_bottom_right=False,
                    body=ft.Stack(
                        width=width,
                        height=height,
                        alignment=ft.alignment.center,
                        controls=[
                            ft.Container(
                                content=self.speed_meter,
                                bottom=0,
                                left=0
                            ),
                            ft.Container(
                                content=self.power_meter,
                                top=0,
                            ),
                            ft.Container(
                                content=self.torque_meter,
                                bottom=0,
                                right=0
                            )
                        ]
                    )
                )
            ]
        )

    def set_power_limit(self, power_max: float, power_warning: float):
        self.power_meter.set_limit(power_max, power_warning)

    def set_torque_limit(self, torque_max: float, torque_warning: float):
        self.torque_meter.set_limit(torque_max, torque_warning)

    def set_speed_limit(self, speed_max: float, speed_warning: float):
        self.speed_meter.set_limit(speed_max, speed_warning)

    def set_power(self, power: float):
        self.power_meter.set_data(power)

    def set_torque(self, torque: float):
        self.torque_meter.set_data(torque)

    def set_speed(self, speed: float):
        self.speed_meter.set_data(speed)

    def set_thrust(self, visible: bool, thrust: float):
        self.thrust_meter.set_data(visible, thrust)

    def did_mount(self):
        self.set_language()

    def before_update(self):
        self.set_language()

    def set_language(self):
        session = self.page.session
        if self.name == "SPS1":
            self.title.value = session.get("lang.common.sps1")
        elif self.name == "SPS2":
            self.title.value = session.get("lang.common.sps2")
