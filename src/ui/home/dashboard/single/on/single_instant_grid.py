import flet as ft
import asyncio
from db.models.data_log import DataLog
from db.models.system_settings import SystemSettings
from db.models.propeller_setting import PropellerSetting
from ui.home.dashboard.single.on.single_instant_power import SingleInstantPower
from ui.home.dashboard.single.on.single_instant_thrust import SingleInstantThrust
from ui.home.dashboard.single.on.single_instant_torque import SingleInstantTorque
from ui.home.dashboard.single.on.single_instant_speed import SingleInstantSpeed
from ui.home.dashboard.limitation.power_limited import PowerLimited
from ui.home.dashboard.limitation.power_unlimited import PowerUnlimited


class SingleInstantGrid(ft.Container):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.expand = True
        self.width = width
        self.height = height

        self.limited_power_value = 0
        self.unlimited_power_value = 0

        self.__load_config()

    def build(self):
        self.power_limited_card = PowerLimited()
        self.power_unlimited_card = PowerUnlimited()
        self.power_card = SingleInstantPower()
        self.thrust_card = SingleInstantThrust(self.display_thrust)
        self.torque_card = SingleInstantTorque()
        self.speed_card = SingleInstantSpeed()

        self.content = ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    expand=False,
                    controls=[
                        self.power_limited_card,
                        self.power_unlimited_card
                    ]
                ),
                ft.Row(
                    expand=True,
                    controls=[
                        self.power_card,
                        self.thrust_card
                    ]
                ),
                ft.Row(
                    expand=True,
                    controls=[
                        self.torque_card,
                        self.speed_card
                    ])
            ]
        )

    def did_mount(self):
        self.power_limited_card.set_value(self.limited_power_value)
        self.power_unlimited_card.set_value(self.unlimited_power_value)
        self._task = self.page.run_task(self.__load_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    def __load_config(self):
        system_settings = SystemSettings.select().order_by(
            SystemSettings.id.desc()).first()

        if system_settings is not None:
            self.display_thrust = system_settings.display_thrust
            self.limited_power_value = system_settings.eexi_limited_power

        propeller_settings = PropellerSetting.select().order_by(
            PropellerSetting.id.desc()).first()
        if propeller_settings is not None:
            self.unlimited_power_value = propeller_settings.shaft_power_of_mcr_operating_point

    async def __load_data(self):
        while True:
            print("load data")
            data_log = DataLog.select(
                DataLog.power,
                DataLog.revolution,
                DataLog.torque,
                DataLog.thrust
            ).order_by(
                DataLog.id.desc()).where(
                DataLog.name == "SPS1"
            ).first()

            if data_log is not None:
                self.power_card.set_value(data_log.power)
                self.thrust_card.set_value(data_log.thrust)
                self.torque_card.set_value(data_log.torque)
                self.speed_card.set_value(data_log.revolution)

            await asyncio.sleep(1)
