import asyncio
import flet as ft

from ui.home.dashboard.dual.on.dual_instant_grid import DualInstantGrid
from ui.home.dashboard.dual.dual_power_chart import DualPowerChart
from db.models.data_log import DataLog
from ui.home.dashboard.eexi.eexi_limited_power import EEXILimitedPower
from db.models.propeller_setting import PropellerSetting
from db.models.system_settings import SystemSettings


class DualShaPoLiOn(ft.Container):
    def __init__(self):
        super().__init__()
        self.__load_config()

    def build(self):
        w = self.page.window.width * 0.5
        h = self.page.window.height * 0.5

        self.eexi_limited_power = EEXILimitedPower(w, h)

        self.instant_grid = DualInstantGrid()

        self.bottom = DualPowerChart()

        self.content = ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    expand=True,
                    controls=[
                        self.eexi_limited_power,
                        self.instant_grid
                    ]),
                self.bottom
            ]
        )

    async def __load_data(self):
        while True:
            data_log_sps1 = DataLog.select(
                DataLog.power,
                DataLog.revolution,
                DataLog.torque,
                DataLog.thrust
            ).where(
                DataLog.name == "SPS1"
            ).order_by(DataLog.id.desc()).first()

            data_log_sps2 = DataLog.select(
                DataLog.power,
                DataLog.revolution,
                DataLog.torque,
                DataLog.thrust
            ).where(
                DataLog.name == "SPS2"
            ).order_by(DataLog.id.desc()).first()

            self.instant_grid.set_power_values(
                data_log_sps1.power, data_log_sps2.power
            )

            self.instant_grid.set_speed_values(
                data_log_sps1.revolution, data_log_sps2.revolution
            )

            self.instant_grid.set_torque_values(
                data_log_sps1.torque, data_log_sps2.torque
            )

            self.instant_grid.set_thrust_values(
                data_log_sps1.thrust, data_log_sps2.thrust
            )

            self.eexi_limited_power.set_value(
                data_log_sps1.power + data_log_sps2.power
            )

            await asyncio.sleep(1)

    def __load_config(self):
        propeller_settings = PropellerSetting.get_or_none()
        if propeller_settings is None:
            return

        system_settings = SystemSettings.get_or_none()
        if system_settings is None:
            return

        self.limited_power_normal = system_settings.eexi_limited_power * 0.9
        self.limited_power_warning = system_settings.eexi_limited_power
        self.unlimited_power = propeller_settings.shaft_power_of_mcr_operating_point

    def did_mount(self):
        self.eexi_limited_power.set_config(
            self.limited_power_normal * 2,
            self.limited_power_warning * 2,
            self.unlimited_power * 2
        )
        self._task = self.page.run_task(self.__load_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()
