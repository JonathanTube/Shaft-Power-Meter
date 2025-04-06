import asyncio
import flet as ft

from ui.home.dashboard.sps_dual.on.dual_instant_grid import DualInstantGrid
from db.models.data_log import DataLog
from ui.home.dashboard.eexi.eexi_limited_power import EEXILimitedPower
from db.models.propeller_setting import PropellerSetting
from db.models.system_settings import SystemSettings
from ui.home.dashboard.chart.single_power_line import SinglePowerLine
from db.models.preference import Preference


class DualShaPoLiOn(ft.Container):
    def __init__(self):
        super().__init__()
        self.__load_config()

    def build(self):
        w = self.page.window.width * 0.5
        h = self.page.window.height * 0.5

        self.eexi_limited_power = EEXILimitedPower(w, h)

        self.instant_grid = DualInstantGrid(self.display_thrust)

        self.power_chart_sps1 = SinglePowerLine(
            name="SPS1",
            max_y=self.unlimited_power,
            sha_po_li=True,
            threshold=self.limited_power_warning,
            unit=self.system_unit
        )

        self.power_chart_sps2 = SinglePowerLine(
            name="SPS2",
            max_y=self.unlimited_power,
            sha_po_li=True,
            threshold=self.limited_power_warning,
            unit=self.system_unit
        )

        self.content = ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    expand=True,
                    controls=[
                        self.eexi_limited_power,
                        self.instant_grid
                    ]),
                ft.Row(
                    expand=True,
                    controls=[
                        self.power_chart_sps1,
                        self.power_chart_sps2
                    ]
                )
            ]
        )

    async def __load_data(self):
        while True:
            sps1_data_logs = DataLog.select(
                DataLog.utc_time,
                DataLog.power,
                DataLog.speed,
                DataLog.torque,
                DataLog.thrust
            ).where(
                DataLog.name == "SPS1"
            ).order_by(DataLog.id.desc()).limit(50)

            sps2_data_logs = DataLog.select(
                DataLog.utc_time,
                DataLog.power,
                DataLog.speed,
                DataLog.torque,
                DataLog.thrust
            ).where(
                DataLog.name == "SPS2"
            ).order_by(DataLog.id.desc()).limit(50)

            sps1_power = sps1_data_logs[0].power if len(
                sps1_data_logs) > 0 else 0
            sps2_power = sps2_data_logs[0].power if len(
                sps2_data_logs) > 0 else 0
            sps1_speed = sps1_data_logs[0].speed if len(
                sps1_data_logs) > 0 else 0
            sps2_speed = sps2_data_logs[0].speed if len(
                sps2_data_logs) > 0 else 0
            sps1_torque = sps1_data_logs[0].torque if len(
                sps1_data_logs) > 0 else 0
            sps2_torque = sps2_data_logs[0].torque if len(
                sps2_data_logs) > 0 else 0
            sps1_thrust = sps1_data_logs[0].thrust if len(
                sps1_data_logs) > 0 else 0
            sps2_thrust = sps2_data_logs[0].thrust if len(
                sps2_data_logs) > 0 else 0

            self.instant_grid.set_power_values(sps1_power, sps2_power, self.system_unit)

            self.instant_grid.set_speed_values(sps1_speed, sps2_speed)

            self.instant_grid.set_torque_values(
                sps1_torque, sps2_torque, self.system_unit
            )

            self.instant_grid.set_thrust_values(
                sps1_thrust, sps2_thrust, self.system_unit
            )

            self.eexi_limited_power.set_value(
                sps1_power + sps2_power
            )

            self.power_chart_sps1.update(sps1_data_logs)
            self.power_chart_sps2.update(sps2_data_logs)

            await asyncio.sleep(self.data_refresh_interval)

    def __load_config(self):
        self.display_thrust = False
        self.limited_power_normal = 0
        self.limited_power_warning = 0
        self.unlimited_power = 0

        propeller_settings = PropellerSetting.get()
        system_settings = SystemSettings.get()

        self.display_thrust = system_settings.display_thrust
        self.limited_power_normal = system_settings.eexi_limited_power * 0.9
        self.limited_power_warning = system_settings.eexi_limited_power
        self.unlimited_power = propeller_settings.shaft_power_of_mcr_operating_point

        preference = Preference.get()
        self.data_refresh_interval = preference.data_refresh_interval
        self.system_unit = preference.system_unit

    def did_mount(self):
        self.eexi_limited_power.set_config(
            self.limited_power_normal * 2,
            self.limited_power_warning * 2,
            self.unlimited_power * 2
        )
        self.set_language()
        self._task = self.page.run_task(self.__load_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    def before_update(self):
        self.set_language()

    def set_language(self):
        self.power_chart_sps1.set_name(
            self.page.session.get("lang.common.sps1"))
        self.power_chart_sps2.set_name(
            self.page.session.get("lang.common.sps2"))
