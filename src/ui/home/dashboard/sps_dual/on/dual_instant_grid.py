import logging
import flet as ft

from ui.home.dashboard.limitation.power_limited import PowerLimited
from ui.home.dashboard.limitation.power_unlimited import PowerUnlimited
from ui.home.dashboard.sps_dual.on.dual_instant_power import DualInstantPower
from ui.home.dashboard.sps_dual.on.dual_instant_speed import DualInstantSpeed
from ui.home.dashboard.sps_dual.on.dual_instant_torque import DualInstantTorque
from ui.home.dashboard.sps_dual.on.dual_instant_thrust import DualInstantThrust


class DualInstantGrid(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def build(self):
        try:
            self.power_limited_card = PowerLimited()
            self.power_unlimited_card = PowerUnlimited()
            self.dual_instant_power = DualInstantPower()
            self.dual_instant_speed = DualInstantSpeed()
            self.dual_instant_torque = DualInstantTorque()
            self.dual_instant_thrust = DualInstantThrust()
            controls = [
                ft.Row(
                    controls=[self.power_limited_card, self.power_unlimited_card]
                ),
                ft.Row(
                    expand=True,
                    controls=[self.dual_instant_power, self.dual_instant_thrust]
                ),
                ft.Row(
                    expand=True,
                    controls=[self.dual_instant_torque, self.dual_instant_speed]
                )
            ]
            self.content = ft.Column(expand=True, controls=controls)
        except:
            logging.exception('exception occured at DualInstantGrid.build')



    def reload(self):
        try:
            self.dual_instant_power.reload()
            self.dual_instant_speed.reload()
            self.dual_instant_torque.reload()
            self.dual_instant_thrust.reload()
        except:
            logging.exception('exception occured at DualInstantGrid.reload')

