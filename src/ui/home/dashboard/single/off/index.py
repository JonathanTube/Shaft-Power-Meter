import flet as ft
from db.models.data_log import DataLog
import asyncio
from db.models.limitations import Limitations
from ui.home.dashboard.single.off.single_meters import SingleMeters
from ui.home.dashboard.chart.power_line_chart import PowerLineChart
from ui.home.dashboard.thrust.thrust_power import ThrustPower


class SingleShaPoLiOff(ft.Stack):
    def __init__(self):
        super().__init__()

        self.power_max = 0
        self.power_warning = 0
        self.speed_max = 0
        self.speed_warning = 0
        self.torque_max = 0
        self.torque_warning = 0

        self.__load_settings()

    def build(self):
        self.thrust_power = ThrustPower()

        self.single_meters = SingleMeters(
            self.power_max, self.power_warning,
            self.speed_max, self.speed_warning,
            self.torque_max, self.torque_warning
        )

        self.power_line_chart = PowerLineChart(self.speed_max)

        self.controls = [
            self.thrust_power,
            ft.Column(
                expand=True,
                spacing=20,
                alignment=ft.alignment.center,
                controls=[
                    self.single_meters,
                    self.power_line_chart
                ]
            )
        ]

    def did_mount(self):
        self._task = self.page.run_task(self.__load_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    def __load_settings(self):
        limitations = Limitations.get_or_none()
        if limitations:
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
                DataLog.name == "SPS1").order_by(DataLog.id.desc()).limit(10)

            if len(data_logs) > 0:
                self.single_meters.set_data(
                    data_logs[0].revolution, data_logs[0].power, data_logs[0].torque
                )
                self.thrust_power.set_data(data_logs[0].thrust)

                # update chart
                data_list = []
                for data_log in data_logs:
                    data_list.append([
                        data_log.utc_time.strftime('%H:%M:%S'),
                        data_log.power
                    ])

                self.power_line_chart.update(data_list)

            await asyncio.sleep(1)
