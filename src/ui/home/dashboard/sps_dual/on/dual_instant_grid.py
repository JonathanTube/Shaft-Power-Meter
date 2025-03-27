import flet as ft

from ui.home.dashboard.sps_dual.on.dual_instant_power import DualInstantPower
from ui.home.dashboard.sps_dual.on.dual_instant_speed import DualInstantSpeed
from ui.home.dashboard.sps_dual.on.dual_instant_torque import DualInstantTorque
from ui.home.dashboard.sps_dual.on.dual_instant_thrust import DualInstantThrust


class DualInstantGrid(ft.Container):
    def __init__(self, display_thrust: bool = True):
        super().__init__()
        self.expand = True
        self.display_thrust = display_thrust

    def build(self):
        self.dual_instant_power = DualInstantPower()
        self.dual_instant_speed = DualInstantSpeed()
        self.dual_instant_torque = DualInstantTorque()
        self.dual_instant_thrust = DualInstantThrust(self.display_thrust)
        controls = [
            ft.Row(
                expand=True,
                controls=[
                    self.dual_instant_power,
                    self.dual_instant_thrust
                ]
            ),
            ft.Row(
                expand=True,
                controls=[
                    self.dual_instant_torque,
                    self.dual_instant_speed
                ]
            )
        ]
        self.content = ft.Column(
            expand=True,
            controls=controls
        )

    def set_power_values(self, power_sps1_value: float, power_sps2_value: float):
        self.dual_instant_power.set_data(power_sps1_value, power_sps2_value)

    def set_speed_values(self, speed_sps1_value: float, speed_sps2_value: float):
        self.dual_instant_speed.set_data(speed_sps1_value, speed_sps2_value)

    def set_torque_values(self, torque_sps1_value: float, torque_sps2_value: float):
        self.dual_instant_torque.set_data(torque_sps1_value, torque_sps2_value)

    def set_thrust_values(self, thrust_sps1_value: float, thrust_sps2_value: float):
        self.dual_instant_thrust.set_data(thrust_sps1_value, thrust_sps2_value)
