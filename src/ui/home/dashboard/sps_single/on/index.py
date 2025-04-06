import flet as ft

from ui.home.dashboard.chart.single_power_line import SinglePowerLine
from ui.home.dashboard.eexi.eexi_limited_power import EEXILimitedPower
from ui.home.dashboard.sps_single.on.single_instant_grid import SingleInstantGrid
from db.models.propeller_setting import PropellerSetting
from db.models.system_settings import SystemSettings
from db.models.data_log import DataLog
from db.models.preference import Preference
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

        self.power_line_chart = SinglePowerLine(
            max_y=self.unlimited_power,
            sha_po_li=True,
            threshold=self.limited_power_warning,
            unit=self.system_unit
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
        if not self.display_thrust:
            self.instant_value_grid.hide_thrust()

        self.eexi_limited_power.set_config(
            self.limited_power_normal,
            self.limited_power_warning,
            self.unlimited_power
        )
        self.instant_value_grid.set_limit(
            self.limited_power_warning,
            self.unlimited_power,
            self.system_unit
        )
        self.set_language()
        self._task = self.page.run_task(self.__load_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    def __load_config(self):
        self.display_thrust = False
        self.limited_power_normal = 0
        self.limited_power_warning = 0
        self.unlimited_power = 0
        self.system_unit = 0

        propeller_settings = PropellerSetting.get()
        self.unlimited_power = propeller_settings.shaft_power_of_mcr_operating_point

        system_settings = SystemSettings.get()
        self.limited_power_normal = system_settings.eexi_limited_power * 0.9
        self.limited_power_warning = system_settings.eexi_limited_power
        self.display_thrust = system_settings.display_thrust

        preference = Preference.get()
        self.data_refresh_interval = preference.data_refresh_interval
        self.system_unit = preference.system_unit

    async def __load_data(self):
        while True:
            data_logs = DataLog.select(
                DataLog.power,
                DataLog.thrust,
                DataLog.torque,
                DataLog.speed,
                DataLog.utc_time
            ).order_by(DataLog.id.desc()).where(DataLog.name == "SPS1").limit(100)
            # print(f'data_logs={data_logs}')
            if len(data_logs) > 0:
                self.eexi_limited_power.set_value(data_logs[0].power)
                self.instant_value_grid.set_data(
                    data_logs[0].power,
                    data_logs[0].thrust,
                    data_logs[0].torque,
                    data_logs[0].speed,
                    self.system_unit
                )
                self.power_line_chart.update(data_logs)
            else:
                self.eexi_limited_power.set_value(0)
                self.instant_value_grid.set_data(0, 0, 0, 0, self.system_unit)
                self.power_line_chart.update([])

            await asyncio.sleep(self.data_refresh_interval)

    def set_language(self):
        session = self.page.session
        self.power_line_chart.set_name(session.get("lang.common.power"))

    def before_update(self):
        self.set_language()
