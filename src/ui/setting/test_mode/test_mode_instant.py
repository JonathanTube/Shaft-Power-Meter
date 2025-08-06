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
        try:
            if self.page and self.page.session:
                self.sps_torque = self.__get_uniform_text("0")
                self.sps_speed = self.__get_uniform_text("0")
                self.sps_thrust = self.__get_uniform_text("0")
                self.sps_power = self.__get_uniform_text("0")
                self.sps_instant_data_card = ft.ResponsiveRow(
                    alignment=ft.alignment.center,
                    controls=[
                        self.__get_uniform_text(self.page.session.get('lang.common.torque')),
                        self.sps_torque,
                        self.__get_uniform_text(self.page.session.get('lang.common.speed')),
                        self.sps_speed,
                        self.__get_uniform_text(self.page.session.get('lang.common.thrust')),
                        self.sps_thrust,
                        self.__get_uniform_text(self.page.session.get('lang.common.power')),
                        self.sps_power
                    ]
                )
                if self.system_settings.amount_of_propeller == 1:
                    self.controls = [
                        CustomCard(f'sps {self.page.session.get('lang.setting.test_mode.instant_mock_data')}', self.sps_instant_data_card)
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
                            f'sps {self.page.session.get('lang.setting.test_mode.instant_mock_data')}',
                            self.sps_instant_data_card
                        ),
                        CustomCard(
                            f'sps2 {self.page.session.get('lang.setting.test_mode.instant_mock_data')}',
                            self.sps2_instant_data_card
                        )
                    ]
        except:
            logging.exception('exception occured at TestModeInstant.build')

    def __get_uniform_text(self, label):
        return ft.Text(value=f"{label}", weight=ft.FontWeight.BOLD, col={"sm": 12, "md": 6})

    async def __refresh_instant(self):
        while self.task_running:
            try:
                if self.sps_speed and self.sps_speed.page:
                    self.sps_speed.value = f'{gdata.configSPS.speed} rpm'
                    self.sps_speed.update()

                if self.sps_torque and self.sps_torque.page:
                    sps_torque_value, sps_torque_unit = UnitParser.parse_torque(gdata.configSPS.torque, self.system_unit)
                    self.sps_torque.value = f'{sps_torque_value} {sps_torque_unit}'
                    self.sps_torque.update()

                if self.sps_thrust and self.sps_thrust.page:
                    sps_thrust_value, sps_thrust_unit = UnitParser.parse_thrust(gdata.configSPS.thrust, self.system_unit)
                    self.sps_thrust.value = f'{sps_thrust_value} {sps_thrust_unit}'
                    self.sps_thrust.update()

                if self.sps_power and self.sps_power.page:
                    sps_power_value, sps_power_unit = UnitParser.parse_power(gdata.configSPS.power, self.system_unit)
                    self.sps_power.value = f'{sps_power_value} {sps_power_unit}'
                    self.sps_power.update()

                if self.system_settings.amount_of_propeller == 2:
                    if self.sps2_speed and self.sps2_speed.page:
                        self.sps2_speed.value = f'{gdata.sps2_speed} rpm'
                        self.sps2_speed.update()

                    if self.sps2_torque and self.sps2_torque.page:
                        sps2_torque_value, sps2_torque_unit = UnitParser.parse_torque(gdata.configSPS2.torque, self.system_unit)
                        self.sps2_torque.value = f'{sps2_torque_value} {sps2_torque_unit}'
                        self.sps2_torque.update()

                    if self.sps2_thrust and self.sps2_thrust.page:
                        sps2_thrust_value, sps2_thrust_unit = UnitParser.parse_thrust(gdata.configSPS2.thrust, self.system_unit)
                        self.sps2_thrust.value = f'{sps2_thrust_value} {sps2_thrust_unit}'
                        self.sps2_thrust.update()

                    if self.sps2_power and self.sps2_power.page:
                        sps2_power_value, sps2_power_unit = UnitParser.parse_power(gdata.configSPS2.power, self.system_unit)
                        self.sps2_power.value = f'{sps2_power_value} {sps2_power_unit}'
                        self.sps2_power.update()
            except:
                logging.exception('exception occured at TestModeInstant.__refresh_instant')
            finally:
                # 默认2s生成一次，和SPS采集一致
                await asyncio.sleep(2)

    def did_mount(self):
        self.task_running = True
        self.task = self.page.run_task(self.__refresh_instant)

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()
