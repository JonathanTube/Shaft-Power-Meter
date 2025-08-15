import flet as ft
import logging
from common.global_data import gdata
from db.models.limitations import Limitations
from db.models.preference import Preference
from db.models.test_mode_conf import TestModeConf
from ui.common.custom_card import CustomCard
from ui.common.toast import Toast
from utils.unit_parser import UnitParser
from task.test_mode_task import test_mode_task


class TestModeRange(ft.Container):
    def __init__(self):
        super().__init__()
        self.conf: TestModeConf = TestModeConf.get()
        preference: Preference = Preference.get()
        self.system_unit: int = preference.system_unit
        limitations: Limitations = Limitations.get()
        self.max_torque: int = limitations.torque_max
        self.max_rpm: float = limitations.speed_max
        self.max_thrust: int = 4000 * 1000

    def build(self):
        try:
            if self.page and self.page.session:
                disabled = not gdata.configTest.test_mode_running
                min_torque_value, min_torque_unit = self.__get_torque_and_unit(self.conf.min_torque)
                max_torque_value, max_torque_unit = self.__get_torque_and_unit(self.conf.max_torque)
                self.start_torque_text = self.__create_range_start_text('lang.setting.test_mode.min_torque', min_torque_value, min_torque_unit)
                self.end_torque_text = self.__create_range_end_text('lang.setting.test_mode.max_torque', max_torque_value, max_torque_unit)
                self.torque_range = ft.RangeSlider(
                    disabled=disabled,
                    expand=True,
                    min=0,
                    max=self.max_torque,
                    start_value=self.conf.min_torque,
                    end_value=self.conf.max_torque,
                    on_change=lambda e: self.__on_torque_change(e)
                )
                self.torque_row = ft.Row(col={"sm": 12}, expand=True, controls=[self.start_torque_text, self.torque_range, self.end_torque_text])

                self.start_speed_text = self.__create_range_start_text('lang.setting.test_mode.min_speed', self.conf.min_speed, 'rpm')
                self.end_speed_text = self.__create_range_end_text('lang.setting.test_mode.max_speed', self.conf.max_speed, 'rpm')
                self.speed_range = ft.RangeSlider(
                    disabled=disabled,
                    expand=True,
                    min=0,
                    max=self.max_rpm,
                    start_value=self.conf.min_speed,
                    end_value=self.conf.max_speed,
                    on_change=lambda e: self.__on_speed_change(e)
                )
                self.speed_row = ft.Row(col={"sm": 12}, expand=True, controls=[self.start_speed_text, self.speed_range, self.end_speed_text])

                min_thrust_value, min_thrust_unit = self.__get_thrust_and_unit(self.conf.min_thrust)
                max_thrust_value, max_thrust_unit = self.__get_thrust_and_unit(self.conf.max_thrust)
                self.start_thrust_text = self.__create_range_start_text('lang.setting.test_mode.min_thrust', min_thrust_value, min_thrust_unit)
                self.end_thrust_text = self.__create_range_end_text('lang.setting.test_mode.max_thrust', max_thrust_value, max_thrust_unit)
                self.thrust_range = ft.RangeSlider(
                    disabled=disabled,
                    expand=True,
                    min=0,
                    max=self.max_thrust,
                    start_value=self.conf.min_thrust,
                    end_value=self.conf.max_thrust,
                    on_change=lambda e: self.__on_thrust_change(e)
                )
                self.thrust_row = ft.Row(col={"sm": 12}, expand=True, controls=[self.start_thrust_text, self.thrust_range, self.end_thrust_text])

                self.custom_card = CustomCard(
                    self.page.session.get("lang.setting.test_mode.customize_data_range"),
                    ft.ResponsiveRow(controls=[
                        self.torque_row,
                        self.speed_row,
                        self.thrust_row
                    ]),
                    col={"xs": 12})
                self.content = self.custom_card
        except:
            logging.exception('exception occured at TestModeRange.build')

    def __create_range_start_text(self, lang, value, unit):
        return ft.Text(color=ft.Colors.GREEN, width=160, value=f'{self.page.session.get(lang)}: {value} {unit}')

    def __create_range_end_text(self, lang, value, unit):
        return ft.Text(color=ft.Colors.RED, width=160, value=f'{self.page.session.get(lang)}: {value} {unit}')

    def __on_torque_change(self, e):
        try:
            min_torque_value, min_torque_unit = self.__get_torque_and_unit(e.control.start_value)
            max_torque_value, max_torque_unit = self.__get_torque_and_unit(e.control.end_value)
            self.start_torque_text.value = f'{self.page.session.get('lang.setting.test_mode.min_torque')}: {min_torque_value} {min_torque_unit}'
            self.start_torque_text.update()
            self.end_torque_text.value = f'{self.page.session.get('lang.setting.test_mode.max_torque')}: {max_torque_value} {max_torque_unit}'
            self.end_torque_text.update()
            self.__save_data()
            test_mode_task.set_torque_range(e.control.start_value, e.control.end_value)
        except:
            logging.exception('exception occured at TestModeRange.__on_torque_change')

    def __on_speed_change(self, e):
        try:
            start_speed_percentage = round(e.control.start_value * 100 / gdata.configPropperCurve.speed_of_mcr, 2)
            end_speed_percentage = round(e.control.end_value * 100 / gdata.configPropperCurve.speed_of_mcr, 2)
            self.start_speed_text.value = f'{self.page.session.get('lang.setting.test_mode.min_speed')}: {int(e.control.start_value)} rpm, {start_speed_percentage}% MCR'
            self.start_speed_text.update()
            self.end_speed_text.value = f'{self.page.session.get('lang.setting.test_mode.max_speed')}: {int(e.control.end_value)} rpm, {end_speed_percentage}% MCR'
            self.end_speed_text.update()
            self.__save_data()
            test_mode_task.set_speed_range(e.control.start_value, e.control.end_value)
        except:
            logging.exception('exception occured at TestModeRange.__on_speed_change')

    def __on_thrust_change(self, e):
        try:
            min_thrust_value, min_thrust_unit = self.__get_thrust_and_unit(e.control.start_value)
            max_thrust_value, max_thrust_unit = self.__get_thrust_and_unit(e.control.end_value)
            self.start_thrust_text.value = f'{self.page.session.get('lang.setting.test_mode.min_thrust')}: {min_thrust_value} {min_thrust_unit}'
            self.start_thrust_text.update()
            self.end_thrust_text.value = f'{self.page.session.get('lang.setting.test_mode.max_thrust')}: {max_thrust_value} {max_thrust_unit}'
            self.end_thrust_text.update()
            self.__save_data()
            test_mode_task.set_thrust_range(e.control.start_value, e.control.end_value)
        except:
            logging.exception('exception occured at TestModeRange.__on_thrust_change')

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

    def __save_data(self):
        try:
            if self.page:
                min_torque = self.torque_range.start_value
                max_torque = self.torque_range.end_value
                min_thrust = self.thrust_range.start_value
                max_thrust = self.thrust_range.end_value
                min_speed = self.speed_range.start_value
                max_speed = self.speed_range.end_value

                TestModeConf.update(
                    min_torque=min_torque,
                    max_torque=max_torque,
                    min_speed=min_speed,
                    max_speed=max_speed,
                    min_thrust=min_thrust,
                    max_thrust=max_thrust
                ).where(TestModeConf.id == self.conf.id).execute()
        except:
            logging.exception("test mode range save data error")
            Toast.show_error(self.page)

    def enable(self):
        self.torque_range.disabled = False
        self.speed_range.disabled = False
        self.thrust_range.disabled = False
        self.update()
        test_mode_task.set_torque_range(int(self.torque_range.start_value), int(self.torque_range.end_value))
        test_mode_task.set_speed_range(int(self.speed_range.start_value), int(self.speed_range.end_value))
        test_mode_task.set_thrust_range(int(self.thrust_range.start_value), int(self.thrust_range.end_value))

    def disable(self):
        self.torque_range.disabled = True
        self.speed_range.disabled = True
        self.thrust_range.disabled = True
        self.update()
