import logging
import flet as ft
from common.global_data import gdata
from db.models.propeller_setting import PropellerSetting
from ui.common.custom_card import CustomCard
from utils.unit_converter import UnitConverter
from ui.common.keyboard import keyboard


class PropellerConfMcr(ft.Container):
    def __init__(self, ps: PropellerSetting):
        super().__init__()
        self.ps = ps
        self.system_unit = gdata.configPreference.system_unit

    def build(self):
        try:
            if self.page and self.page.session:
                self.rpm_of_mcr_operating_point = ft.TextField(
                    label=self.page.session.get("lang.common.speed"),
                    suffix_text='rpm',
                    col={"xs": 6},
                    value=self.ps.rpm_of_mcr_operating_point,
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control)
                )

                shaft_power_value, shaft_power_unit = self.__get_shaft_power()
                self.shaft_power_of_mcr_operating_point = ft.TextField(
                    label=self.page.session.get("lang.common.power"),
                    col={"xs": 6},
                    value=shaft_power_value,
                    suffix_text=shaft_power_unit,
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, "int")
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
            return (round(_shaft_power / 1000), "kW")
        else:
            return (UnitConverter.w_to_shp(_shaft_power), "sHp")

    def save_data(self):
        self.ps.rpm_of_mcr_operating_point = float(self.rpm_of_mcr_operating_point.value)

        shaft_power = int(self.shaft_power_of_mcr_operating_point.value)
        if self.system_unit == 0:
            self.ps.shaft_power_of_mcr_operating_point = shaft_power * 1000
        else:
            self.ps.shaft_power_of_mcr_operating_point = UnitConverter.shp_to_w(shaft_power)

        gdata.configPropperCurve.power_of_mcr = float(self.ps.shaft_power_of_mcr_operating_point)
        gdata.configPropperCurve.speed_of_mcr = int(self.ps.rpm_of_mcr_operating_point)
