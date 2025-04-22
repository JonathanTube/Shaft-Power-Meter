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

    def build(self):
        self.sps1_instant_data_card = ft.ResponsiveRow(
            alignment=ft.alignment.center,
            controls=[
                self.__get_uniform_text(self.page.session.get('lang.common.torque')),
                self.__get_uniform_text("0"),
                self.__get_uniform_text(self.page.session.get('lang.common.speed')),
                self.__get_uniform_text("0"),
                self.__get_uniform_text(self.page.session.get('lang.common.thrust')),
                self.__get_uniform_text("0"),
                self.__get_uniform_text(self.page.session.get('lang.common.revolution')),
                self.__get_uniform_text("0")
            ]
        )
        if self.system_settings.amount_of_propeller == 1:
            self.controls = [
                CustomCard(f'sps1 {self.page.session.get('lang.setting.test_mode.instant_mock_data')}', self.sps1_instant_data_card)
            ]
        else:
            self.sps2_instant_data_card = ft.ResponsiveRow(
                alignment=ft.alignment.center,
                controls=[
                    self.__get_uniform_text(self.page.session.get('lang.common.torque')),
                    self.__get_uniform_text("0"),
                    self.__get_uniform_text(self.page.session.get('lang.common.speed')),
                    self.__get_uniform_text("0"),
                    self.__get_uniform_text(self.page.session.get('lang.common.thrust')),
                    self.__get_uniform_text("0"),
                    self.__get_uniform_text(self.page.session.get('lang.common.revolution')),
                    self.__get_uniform_text("0")
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
        while True:
            sps1_torque = gdata.sps1_torque
            sps1_speed = gdata.sps1_speed
            sps1_thrust = gdata.sps1_thrust
            sps1_revolution = gdata.sps1_rounds
            sps1_torque_value, sps1_torque_unit = UnitParser.parse_torque(sps1_torque, self.system_unit)
            self.sps1_instant_data_card.controls[1].value = f'{sps1_torque_value} {sps1_torque_unit}'
            self.sps1_instant_data_card.controls[3].value = f'{sps1_speed} rpm'
            sps1_thrust_value, sps1_thrust_unit = UnitParser.parse_thrust(sps1_thrust, self.system_unit)
            self.sps1_instant_data_card.controls[5].value = f'{sps1_thrust_value} {sps1_thrust_unit}'
            self.sps1_instant_data_card.controls[7].value = sps1_revolution
            self.sps1_instant_data_card.update()

            if self.system_settings.amount_of_propeller == 2:
                sps2_torque = gdata.sps2_torque
                sps2_speed = gdata.sps2_speed
                sps2_thrust = gdata.sps2_thrust
                sps2_revolution = gdata.sps2_rounds
                sps2_torque_value, sps2_torque_unit = UnitParser.parse_torque(sps2_torque, self.system_unit)
                self.sps2_instant_data_card.controls[1].value = f'{sps2_torque_value} {sps2_torque_unit}'
                self.sps2_instant_data_card.controls[3].value = f'{sps2_speed} rpm'
                sps2_thrust_value, sps2_thrust_unit = UnitParser.parse_thrust(sps2_thrust, self.system_unit)
                self.sps2_instant_data_card.controls[5].value = f'{sps2_thrust_value} {sps2_thrust_unit}'
                self.sps2_instant_data_card.controls[7].value = sps2_revolution
                self.sps2_instant_data_card.update()

            await asyncio.sleep(1)

    def did_mount(self):
        self.task = self.page.run_task(self.__refresh_instant)

    def will_unmount(self):
        if self.task:
            self.task.cancel()
