import flet as ft
from db.models.preference import Preference
from ui.home.dashboard.sps_dual.off.dual_meters import DualMeters
import asyncio
from db.models.data_log import DataLog
from db.models.limitations import Limitations
from db.models.system_settings import SystemSettings
from ui.home.dashboard.chart.dual_power_line import DualPowerLine
from common.global_data import gdata

class DualShaPoLiOff(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

        self.__load_settings()

    def build(self):
        self.sps1_meters = DualMeters(name="sps1")
        self.sps2_meters = DualMeters(name="sps2")
        self.dual_power_line = DualPowerLine(
            max_y=self.power_max, unit=self.system_unit)

        self.content = ft.Column(
            expand=True,
            spacing=10,
            controls=[
                ft.Row(
                    expand=True,
                    spacing=10,
                    controls=[self.sps1_meters, self.sps2_meters]
                ),
                self.dual_power_line
            ]
        )

    def did_mount(self):
        self.sps1_meters.set_power_limit(self.power_max, self.power_warning)
        self.sps1_meters.set_torque_limit(self.torque_max, self.torque_warning)
        self.sps1_meters.set_speed_limit(self.speed_max, self.speed_warning)

        self.sps2_meters.set_power_limit(self.power_max, self.power_warning)
        self.sps2_meters.set_torque_limit(self.torque_max, self.torque_warning)
        self.sps2_meters.set_speed_limit(self.speed_max, self.speed_warning)

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

        limitations = Limitations.get()

        self.speed_max = limitations.speed_max
        self.speed_warning = limitations.speed_warning

        self.power_max = limitations.power_max
        self.power_warning = limitations.power_warning

        self.torque_max = limitations.torque_max
        self.torque_warning = limitations.torque_warning

        system_settings = SystemSettings.get()
        self.display_thrust = system_settings.display_thrust

        preference = Preference.get()
        self.data_refresh_interval = preference.data_refresh_interval
        self.system_unit = preference.system_unit

    async def __load_data(self):
        while True:
            sps1_speed = gdata.sps1_speed
            sps1_power = gdata.sps1_power
            sps1_torque = gdata.sps1_torque
            sps1_thrust = gdata.sps1_thrust
           
            unit = self.system_unit
            display_thrust = self.display_thrust

            self.sps1_meters.set_power(sps1_power, unit)
            self.sps1_meters.set_torque(sps1_torque, unit)
            self.sps1_meters.set_speed(sps1_speed)
            self.sps1_meters.set_thrust(display_thrust, sps1_thrust, unit)

            sps2_speed = gdata.sps1_speed
            sps2_power = gdata.sps1_power
            sps2_torque = gdata.sps1_torque
            sps2_thrust = gdata.sps1_thrust

            self.sps2_meters.set_power(sps2_power, unit)
            self.sps2_meters.set_torque(sps2_torque, unit)
            self.sps2_meters.set_speed(sps2_speed)
            self.sps2_meters.set_thrust(display_thrust, sps2_thrust, unit)

            sps1_data_log = DataLog.select(
                DataLog.utc_date_time,
                DataLog.speed,
                DataLog.power,
                DataLog.torque,
                DataLog.thrust
            ).where(DataLog.name == 'sps1').order_by(DataLog.id.desc()).limit(100)

            sps2_data_log = DataLog.select(
                DataLog.utc_date_time,
                DataLog.speed,
                DataLog.power,
                DataLog.torque,
                DataLog.thrust
            ).where(DataLog.name == 'sps2').order_by(DataLog.id.desc()).limit(100)

            self.dual_power_line.set_data(sps1_data_log, sps2_data_log)

            await asyncio.sleep(self.data_refresh_interval)

    def __get_session(self, key: str):
        return self.page.session.get(key)
