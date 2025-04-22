import flet as ft
from db.models.preference import Preference
from db.models.test_mode_conf import TestModeConf
from ui.common.keyboard import keyboard
from ui.common.custom_card import CustomCard
from ui.common.toast import Toast
from utils.unit_parser import UnitParser


class TestModeRange(CustomCard):
    def __init__(self):
        super().__init__()
        self.conf = TestModeConf.get()
        preference: Preference = Preference.get()
        self.system_unit = preference.system_unit

    def build(self):
        min_torque_value, min_torque_unit = self.__get_torque_and_unit(self.conf.min_torque)
        self.min_torque = ft.TextField(
            col={"sm": 6},
            label=self.page.session.get('lang.setting.test_mode.min_torque'),
            suffix_text=min_torque_unit,
            value=min_torque_value,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        max_torque_value, max_torque_unit = self.__get_torque_and_unit(self.conf.max_torque)
        self.max_torque = ft.TextField(
            col={"sm": 6},
            label=self.page.session.get('lang.setting.test_mode.max_torque'),
            suffix_text=max_torque_unit,
            value=max_torque_value,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.min_speed = ft.TextField(
            col={"sm": 6},
            label=self.page.session.get('lang.setting.test_mode.min_speed'),
            suffix_text='rpm',
            value=self.conf.min_speed,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.max_speed = ft.TextField(
            col={"sm": 6},
            label=self.page.session.get('lang.setting.test_mode.max_speed'),
            suffix_text='rpm',
            value=self.conf.max_speed,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        min_thrust_value, min_thrust_unit = self.__get_thrust_and_unit(self.conf.min_thrust)
        self.min_thrust = ft.TextField(
            col={"sm": 6},
            label=self.page.session.get('lang.setting.test_mode.min_thrust'),
            suffix_text=min_thrust_unit,
            value=min_thrust_value,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        max_thrust_value, max_thrust_unit = self.__get_thrust_and_unit(self.conf.max_thrust)
        self.max_thrust = ft.TextField(
            col={"sm": 6},
            label=self.page.session.get('lang.setting.test_mode.max_thrust'),
            suffix_text=max_thrust_unit,
            value=max_thrust_value,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.min_revolution = ft.TextField(
            col={"sm": 6},
            label=self.page.session.get('lang.setting.test_mode.min_revolution'),
            value=self.conf.min_revolution,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.max_revolution = ft.TextField(
            col={"sm": 6},
            label=self.page.session.get('lang.setting.test_mode.max_revolution'),
            value=self.conf.max_revolution,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.heading = self.page.session.get('lang.setting.test_mode.customize_data_range')
        self.body = ft.ResponsiveRow([
            self.min_torque,
            self.max_torque,
            self.min_speed,
            self.max_speed,
            self.min_thrust,
            self.max_thrust,
            self.min_revolution,
            self.max_revolution
        ])
        super().build()

    def __get_torque_and_unit(self, value) -> tuple[float, str]:
        if self.system_unit == 0:
            return [round(value / 1000, 2), 'kNm']
        else:
            return UnitParser.parse_torque(value, self.system_unit)

    def __get_thrust_and_unit(self, value) -> tuple[float, str]:
        if self.system_unit == 0:
            return [round(value / 1000, 2), 'kN']
        else:
            return UnitParser.parse_thrust(value, self.system_unit)

    def save_data(self):
        try:
            min_torque = self.convert_torque(self.min_torque.value)
            max_torque = self.convert_torque(self.max_torque.value)
            min_thrust = self.convert_thrust(self.min_thrust.value)
            max_thrust = self.convert_thrust(self.max_thrust.value)
            min_rev = int(self.min_revolution.value)
            max_rev = int(self.max_revolution.value)
            min_speed = int(self.min_speed.value)
            max_speed = int(self.max_speed.value)

            TestModeConf.update(
                min_torque=min_torque,
                max_torque=max_torque,
                min_speed=min_speed,
                max_speed=max_speed,
                min_thrust=min_thrust,
                max_thrust=max_thrust,
                min_revolution=min_rev,
                max_revolution=max_rev
            ).where(TestModeConf.id == self.conf.id).execute()
            Toast.show_success(self.page)
        except Exception as e:
            Toast.show_error(self.page, str(e))
