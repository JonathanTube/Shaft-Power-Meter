import flet as ft
from ui.home.dashboard.sps_single.on.single_instant_power import SingleInstantPower
from ui.home.dashboard.sps_single.on.single_instant_thrust import SingleInstantThrust
from ui.home.dashboard.sps_single.on.single_instant_torque import SingleInstantTorque
from ui.home.dashboard.sps_single.on.single_instant_speed import SingleInstantSpeed
from ui.home.dashboard.limitation.power_limited import PowerLimited
from ui.home.dashboard.limitation.power_unlimited import PowerUnlimited


class SingleInstantGrid(ft.Container):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.expand = True
        self.width = width
        self.height = height

    def build(self):
        self.power_limited_card = PowerLimited()
        self.power_unlimited_card = PowerUnlimited()
        self.power_card = SingleInstantPower()
        self.thrust_card = SingleInstantThrust()
        self.torque_card = SingleInstantTorque()
        self.speed_card = SingleInstantSpeed()

        self.content = ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    expand=False,
                    controls=[
                        self.power_limited_card,
                        self.power_unlimited_card
                    ]
                ),
                ft.Row(
                    expand=True,
                    controls=[
                        self.power_card,
                        self.thrust_card
                    ]
                ),
                ft.Row(
                    expand=True,
                    controls=[
                        self.torque_card,
                        self.speed_card
                    ])
            ]
        )

    def hide_thrust(self):
        self.thrust_card.visible = False
        self.thrust_card.update()

    def set_limit(self, limited_power: float, unlimited_power: float):
        self.power_limited_card.set_value(limited_power)
        self.power_unlimited_card.set_value(unlimited_power)

    def set_data(self, power: float, thrust: float, torque: float, speed: float):
        self.power_card.set_value(power)
        self.thrust_card.set_value(thrust)
        self.torque_card.set_value(torque)
        self.speed_card.set_value(speed)
