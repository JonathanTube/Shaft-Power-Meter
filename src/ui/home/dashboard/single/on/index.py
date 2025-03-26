import flet as ft

from ui.home.dashboard.chart.power_line_chart import PowerLineChart
from ui.home.dashboard.eexi.eexi_limited_power import EEXILimitedPower
from ui.home.dashboard.single.on.single_instant_grid import SingleInstantGrid
from db.models.propeller_setting import PropellerSetting
from db.models.system_settings import SystemSettings
from db.models.data_log import DataLog
import asyncio


class SingleShaPoLiOn(ft.Container):
    def __init__(self):
        super().__init__()
        self.__load_config()

    def build(self):
        w = self.page.window.width * 0.5
        h = self.page.window.height * 0.5

        self.eexi_limited_power = EEXILimitedPower(w, h)
        self.instant_value_grid = SingleInstantGrid(w, h)

        self.power_line_chart = PowerLineChart(
            max_y=self.unlimited_power,
            sha_po_li=True,
            threshold=self.limited_power_warning
        )
        self.content = ft.Column(
            controls=[
                ft.Row(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        self.eexi_limited_power,
                        self.instant_value_grid
                    ]
                ),
                self.power_line_chart
            ],
            expand=True
        )

    def did_mount(self):
        self.eexi_limited_power.set_config(
            self.limited_power_normal,
            self.limited_power_warning,
            self.unlimited_power
        )
        self._task = self.page.run_task(self.__load_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    def __load_config(self):
        propeller_settings = PropellerSetting.get_or_none()
        if propeller_settings is not None:
            self.unlimited_power = propeller_settings.shaft_power_of_mcr_operating_point

        system_settings = SystemSettings.get_or_none()
        if system_settings is not None:
            self.limited_power_normal = system_settings.eexi_limited_power * 0.9
            self.limited_power_warning = system_settings.eexi_limited_power

    async def __load_data(self):
        while True:
            data_logs = DataLog.select(DataLog.power, DataLog.utc_time).order_by(
                DataLog.id.desc()).where(DataLog.name == "SPS1").limit(10)
            print(f'data_logs={data_logs}')
            if len(data_logs) > 0:
                self.eexi_limited_power.set_value(data_logs[0].power)

                data_list = []
                for data_log in data_logs:
                    data_list.append([
                        data_log.utc_time.strftime('%H:%M:%S'),
                        data_log.power
                    ])

                self.power_line_chart.update(data_list)

            await asyncio.sleep(1)
