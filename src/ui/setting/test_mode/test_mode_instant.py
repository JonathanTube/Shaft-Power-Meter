import logging
import flet as ft
import asyncio
from db.models.system_settings import SystemSettings
from db.models.preference import Preference
from ui.common.custom_card import CustomCard
from common.global_data import gdata
from utils.unit_parser import UnitParser


class TestModeInstant(ft.ResponsiveRow):
    def __init__(self):
        super().__init__()
        self.system_settings: SystemSettings = SystemSettings.get()
        preference: Preference = Preference.get()
        self.system_unit = preference.system_unit

        self.task = None
        self.task_running = False

    def build(self):
        self.sps1_torque = self.__get_uniform_text("0")
        self.sps1_speed = self.__get_uniform_text("0")
        self.sps1_thrust = self.__get_uniform_text("0")
        self.sps1_power = self.__get_uniform_text("0")
        self.sps1_instant_data_card = ft.ResponsiveRow(
            alignment=ft.alignment.center,
            controls=[
                self.__get_uniform_text(self.page.session.get('lang.common.torque')),
                self.sps1_torque,
                self.__get_uniform_text(self.page.session.get('lang.common.speed')),
                self.sps1_speed,
                self.__get_uniform_text(self.page.session.get('lang.common.thrust')),
                self.sps1_thrust,
                self.__get_uniform_text(self.page.session.get('lang.common.power')),
                self.sps1_power
            ]
        )
        if self.system_settings.amount_of_propeller == 1:
            self.controls = [
                CustomCard(f'sps1 {self.page.session.get('lang.setting.test_mode.instant_mock_data')}', self.sps1_instant_data_card)
            ]
        else:
            self.sps2_torque = self.__get_uniform_text("0")
            self.sps2_speed = self.__get_uniform_text("0")
            self.sps2_thrust = self.__get_uniform_text("0")
            self.sps2_power = self.__get_uniform_text("0")
            self.sps2_instant_data_card = ft.ResponsiveRow(
                alignment=ft.alignment.center,
                controls=[
                    self.__get_uniform_text(self.page.session.get('lang.common.torque')),
                    self.sps2_torque,
                    self.__get_uniform_text(self.page.session.get('lang.common.speed')),
                    self.sps2_speed,
                    self.__get_uniform_text(self.page.session.get('lang.common.thrust')),
                    self.sps2_thrust,
                    self.__get_uniform_text(self.page.session.get('lang.common.power')),
                    self.sps2_power
                ]
            )

            self.controls = [
                CustomCard(
                    f'sps1 {self.page.session.get('lang.setting.test_mode.instant_mock_data')}',
                    self.sps1_instant_data_card
                ),
                CustomCard(
                    f'sps2 {self.page.session.get('lang.setting.test_mode.instant_mock_data')}',
                    self.sps2_instant_data_card
                )
            ]

    def __get_uniform_text(self, label):
        return ft.Text(value=f"{label}", weight=ft.FontWeight.BOLD, col={"sm": 12, "md": 6})

    async def __refresh_instant(self):
        while self.task_running:
            try:
                self.sps1_speed.value = f'{gdata.sps1_speed} rpm'
                self.sps1_speed.update()

                sps1_torque_value, sps1_torque_unit = UnitParser.parse_torque(gdata.sps1_torque, self.system_unit)
                self.sps1_torque.value = f'{sps1_torque_value} {sps1_torque_unit}'
                self.sps1_torque.update()

                sps1_thrust_value, sps1_thrust_unit = UnitParser.parse_thrust(gdata.sps1_thrust, self.system_unit)
                self.sps1_thrust.value = f'{sps1_thrust_value} {sps1_thrust_unit}'
                self.sps1_thrust.update()

                sps1_power_value, sps1_power_unit = UnitParser.parse_power(gdata.sps1_power, self.system_unit)
                self.sps1_power.value = f'{sps1_power_value} {sps1_power_unit}'
                self.sps1_power.update()

                if self.system_settings.amount_of_propeller == 2:
                    self.sps2_speed.value = f'{gdata.sps2_speed} rpm'
                    self.sps2_speed.update()

                    sps2_torque_value, sps2_torque_unit = UnitParser.parse_torque(gdata.sps2_torque, self.system_unit)

                    self.sps2_torque.value = f'{sps2_torque_value} {sps2_torque_unit}'
                    self.sps2_torque.update()

                    sps2_thrust_value, sps2_thrust_unit = UnitParser.parse_thrust(gdata.sps2_thrust, self.system_unit)
                    self.sps2_thrust.value = f'{sps2_thrust_value} {sps2_thrust_unit}'
                    self.sps2_thrust.update()

                    sps2_power_value, sps2_power_unit = UnitParser.parse_power(gdata.sps2_power, self.system_unit)
                    self.sps2_power.value = f'{sps2_power_value} {sps2_power_unit}'
                    self.sps2_power.update()
            except Exception as e:
                logging.exception(e)

            await asyncio.sleep(1)

    def did_mount(self):
        self.task_running = True
        self.task = self.page.run_task(self.__refresh_instant)

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()
