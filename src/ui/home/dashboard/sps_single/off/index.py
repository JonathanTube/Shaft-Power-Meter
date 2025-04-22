import flet as ft
from db.models.data_log import DataLog
from db.models.limitations import Limitations
from db.models.preference import Preference
from ui.home.dashboard.sps_single.off.single_meters import SingleMeters
from ui.home.dashboard.chart.single_power_line import SinglePowerLine
from ui.home.dashboard.thrust.thrust_power import ThrustPower
from db.models.system_settings import SystemSettings
from common.global_data import gdata


class SingleShaPoLiOff(ft.Stack):
    def __init__(self):
        super().__init__()
        self.__load_settings()

    def __load_settings(self):
        system_settings: SystemSettings = SystemSettings.get()
        self.display_thrust = system_settings.display_thrust

        limitations: Limitations = Limitations.get()
        self.speed_max = limitations.speed_max
        self.speed_warning = limitations.speed_warning
        self.power_max = limitations.power_max
        self.power_warning = limitations.power_warning
        self.torque_max = limitations.torque_max
        self.torque_warning = limitations.torque_warning

        preference: Preference = Preference.get()
        self.system_unit = preference.system_unit

    def build(self):
        self.thrust_power = ThrustPower()

        self.single_meters = SingleMeters()

        self.power_line_chart = SinglePowerLine(name=self.page.session.get(
            "lang.common.power"), max_y=self.power_max, unit=self.system_unit)

        self.controls = [
            self.thrust_power,
            ft.Column(
                expand=True,
                spacing=10,
                alignment=ft.alignment.center,
                controls=[
                    self.single_meters,
                    self.power_line_chart
                ]
            )
        ]

    def did_mount(self):
        self.single_meters.set_power_limit(self.power_max, self.power_warning)
        self.single_meters.set_torque_limit(self.torque_max, self.torque_warning)
        self.single_meters.set_speed_limit(self.speed_max, self.speed_warning)

    def load_data(self):
        speed = gdata.sps1_speed
        power = gdata.sps1_power
        torque = gdata.sps1_torque
        thrust = gdata.sps1_thrust

        system_unit = self.system_unit
        display_thrust = self.display_thrust

        self.single_meters.set_data(speed, power, torque, system_unit)
        self.thrust_power.set_data(display_thrust, thrust, system_unit)

        data_logs = DataLog.select(
            DataLog.utc_date_time,
            DataLog.speed,
            DataLog.power,
            DataLog.torque,
            DataLog.thrust
        ).where(DataLog.name == "sps1").order_by(DataLog.id.desc()).limit(100)

        self.power_line_chart.update(data_logs)
