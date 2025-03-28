import flet as ft
from db.models.data_log import DataLog
import asyncio
from db.models.limitations import Limitations
from ui.home.dashboard.sps_single.off.single_meters import SingleMeters
from ui.home.dashboard.chart.single_power_line import SinglePowerLine
from ui.home.dashboard.thrust.thrust_power import ThrustPower
from db.models.system_settings import SystemSettings


class SingleShaPoLiOff(ft.Stack):
    def __init__(self):
        super().__init__()

        self.__load_settings()

    def build(self):
        self.thrust_power = ThrustPower()

        self.single_meters = SingleMeters()

        self.power_line_chart = SinglePowerLine(max_y=self.speed_max)

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
        self.single_meters.set_power_limit(
            self.power_max, self.power_warning
        )
        self.single_meters.set_torque_limit(
            self.torque_max, self.torque_warning
        )
        self.single_meters.set_speed_limit(
            self.speed_max, self.speed_warning
        )
        self.set_language()
        self._task = self.page.run_task(self.__load_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    def __load_settings(self):
        self.speed_max = 0
        self.speed_warning = 0
        self.power_max = 0
        self.power_warning = 0
        self.torque_max = 0
        self.torque_warning = 0
        self.display_thrust = False

        system_settings = SystemSettings.get()
        self.display_thrust = system_settings.display_thrust

        limitations = Limitations.get()
        self.speed_max = limitations.speed_max
        self.speed_warning = limitations.speed_warning

        self.power_max = limitations.power_max
        self.power_warning = limitations.power_warning

        self.torque_max = limitations.torque_max
        self.torque_warning = limitations.torque_warning

    async def __load_data(self):
        while True:
            data_logs = DataLog.select(
                DataLog.utc_time,
                DataLog.revolution,
                DataLog.power,
                DataLog.torque,
                DataLog.thrust
            ).where(
                DataLog.name == "SPS1").order_by(DataLog.id.desc()).limit(100)

            if len(data_logs) > 0:
                self.single_meters.set_data(
                    data_logs[0].revolution, data_logs[0].power, data_logs[0].torque
                )
                self.thrust_power.set_data(
                    self.display_thrust, data_logs[0].thrust)
                self.power_line_chart.update(data_logs)

            await asyncio.sleep(1)

    def set_language(self):
        session = self.page.session
        self.power_line_chart.set_name(session.get("lang.common.power"))

    def before_update(self):
        self.set_language()

