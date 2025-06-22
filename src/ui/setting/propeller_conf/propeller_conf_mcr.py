import logging
import flet as ft
from common.global_data import gdata
from db.models.preference import Preference
from db.models.propeller_setting import PropellerSetting
from ui.common.custom_card import CustomCard
from utils.unit_converter import UnitConverter
from ui.common.keyboard import keyboard


class PropellerConfMcr(CustomCard):
    def __init__(self, ps: PropellerSetting):
        super().__init__()
        self.ps = ps
        preference: Preference = Preference.get()
        self.system_unit = preference.system_unit

    def build(self):
        try:
            self.rpm_of_mcr_operating_point = ft.TextField(
                label=self.page.session.get("lang.common.speed"),
                suffix_text='rpm',
                col={"md": 6},
                value=self.ps.rpm_of_mcr_operating_point,
                read_only=True,
                can_request_focus=False,
                on_click=lambda e: keyboard.open(e.control, type='int')
            )

            shaft_power_value, shaft_power_unit = self.__get_shaft_power()
            self.shaft_power_of_mcr_operating_point = ft.TextField(
                label=self.page.session.get("lang.common.power"),
                col={"md": 6},
                value=shaft_power_value,
                suffix_text=shaft_power_unit,
                read_only=True,
                can_request_focus=False,
                on_click=lambda e: keyboard.open(e.control)
            )

            self.custom_card = CustomCard(
                self.page.session.get("lang.setting.mcr_operating_point"),
                ft.ResponsiveRow(controls=[
                    self.rpm_of_mcr_operating_point,
                    self.shaft_power_of_mcr_operating_point
                ]),
                col={"xs": 12})
            self.content = self.custom_card
        except:
            logging.exception('exception occured at PropellerConfMcr.build')

    def __get_shaft_power(self) -> tuple[float, str]:
        _shaft_power = float(self.ps.shaft_power_of_mcr_operating_point)
        if self.system_unit == 0:
            return (_shaft_power / 1000, "kW")
        else:
            return (UnitConverter.w_to_shp(_shaft_power), "sHp")

    def save_data(self):
        self.ps.rpm_of_mcr_operating_point = self.rpm_of_mcr_operating_point.value

        shaft_power = float(self.shaft_power_of_mcr_operating_point.value)
        if self.system_unit == 0:
            self.ps.shaft_power_of_mcr_operating_point = shaft_power * 1000
        else:
            self.ps.shaft_power_of_mcr_operating_point = UnitConverter.shp_to_w(shaft_power)

        gdata.power_of_mcr = float(self.ps.shaft_power_of_mcr_operating_point)
        gdata.speed_of_mcr = int(self.ps.rpm_of_mcr_operating_point)
