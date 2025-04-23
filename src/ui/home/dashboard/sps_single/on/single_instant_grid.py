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

    def reload(self):
        self.power_card.reload()
        self.thrust_card.reload()
        self.torque_card.reload()
        self.speed_card.reload()
