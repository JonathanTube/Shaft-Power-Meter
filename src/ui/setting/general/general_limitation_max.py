import logging
import flet as ft

from db.models.limitations import Limitations
from ui.common.custom_card import CustomCard
from utils.unit_converter import UnitConverter
from ui.common.keyboard import keyboard
from common.global_data import gdata


class GeneralLimitationMax(ft.Container):
    def __init__(self, system_unit: int):
        super().__init__()
        self.expand = True
        self.col = {"md": 6}
        self.system_unit = system_unit

    def build(self):
        try:
            if self.page and self.page.session:
                self.speed_max = ft.TextField(
                    suffix_text="rpm",
                    label=self.page.session.get("lang.common.speed"),
                    value=gdata.configLimitation.speed_max,
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control))

                self.torque_max = ft.TextField(
                    suffix_text="kNm",
                    label=self.page.session.get("lang.common.torque"),
                    value=gdata.configLimitation.torque_max,
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, "int"))

                self.power_max = ft.TextField(
                    suffix_text="kW",
                    label=self.page.session.get("lang.common.power"),
                    value=gdata.configLimitation.power_max,
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, "int"))

                self.custom_card = CustomCard(
                    self.page.session.get("lang.setting.maximum_limitations"),
                    ft.Column(controls=[self.speed_max, self.torque_max, self.power_max])
                )
                self.content = self.custom_card
        except:
            logging.exception('exception occured at GeneralLimitationMax.build')

    def reset(self):
        try:
            if self.page and self.page.session:
                s = self.page.session
                if self.speed_max is not None:
                    self.speed_max.label = s.get("lang.common.speed")

                if self.torque_max is not None:
                    self.torque_max.label = s.get("lang.common.torque")

                if self.power_max is not None:
                    self.power_max.label = s.get("lang.common.power")

                if self.custom_card is not None:
                    self.custom_card.set_title(s.get("lang.setting.maximum_limitations"))
        except:
            logging.exception('exception occured at GeneralLimitationMax.before_update')

    def update_unit(self, system_unit: int):
        try:
            if self.page:
                self.system_unit = system_unit
                torque_limit = gdata.configLimitation.torque_max
                power_limit = gdata.configLimitation.power_max
                if self.system_unit == 0:

                    if self.torque_max is not None:
                        self.torque_max.suffix_text = "kNm"
                        self.torque_max.value = round(torque_limit / 1000)

                    if self.power_max is not None:
                        self.power_max.suffix_text = "kW"
                        self.power_max.value = round(power_limit / 1000)

                elif self.system_unit == 1:

                    if self.torque_max is not None:
                        self.torque_max.suffix_text = "Tm"
                        self.torque_max.value = UnitConverter.nm_to_tm(torque_limit)

                    if self.power_max is not None:
                        self.power_max.suffix_text = "sHp"
                        self.power_max.value = UnitConverter.w_to_shp(power_limit)

                if self.content and self.content.page:
                    self.content.update()
        except:
            logging.exception('exception occured at GeneralLimitationMax.update_unit')

    def save_data(self, user_id: int):
        # save
        max_speed = float(self.speed_max.value)
        max_torque = int(self.torque_max.value)
        max_power = int(self.power_max.value)

        if self.system_unit == 0:
            # kNm to Nm
            max_torque = UnitConverter.knm_to_nm(max_torque)
            # kw to w
            max_power = UnitConverter.kw_to_w(max_power)
        elif self.system_unit == 1:
            # Tm to Nm
            max_torque = UnitConverter.tm_to_nm(max_torque)
            # shp to w
            max_power = UnitConverter.shp_to_w(max_power)

        Limitations.update(power_max=max_power, torque_max=max_torque, speed_max=max_speed).execute()
        gdata.configLimitation.set_default_value()

    def did_mount(self):
        self.update_unit(self.system_unit)
