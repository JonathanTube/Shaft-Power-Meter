import logging
import flet as ft

from ui.common.custom_card import CustomCard
from db.models.limitations import Limitations
from utils.unit_converter import UnitConverter
from ui.common.keyboard import keyboard
from common.global_data import gdata


class GeneralLimitationWarning(ft.Container):
    def __init__(self, system_unit: int):
        super().__init__()
        self.expand = True
        self.col = {"md": 6}
        self.system_unit = system_unit

    def build(self):
        try:
            if self.page and self.page.session:
                self.torque_warning = ft.TextField(
                    suffix_text="kNm",
                    label=self.page.session.get("lang.common.torque"),
                    value=gdata.configLimitation.torque_warning,
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, "int"))

                self.speed_warning = ft.TextField(
                    suffix_text="rpm",
                    label=self.page.session.get("lang.common.speed"),
                    value=gdata.configLimitation.speed_warning,
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control))

                self.power_warning = ft.TextField(
                    suffix_text="kW",
                    label=self.page.session.get("lang.common.power"),
                    value=gdata.configLimitation.power_warning,
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, "int"))

                self.custom_card = CustomCard(
                    self.page.session.get("lang.setting.warning_limitations"),
                    ft.Column(controls=[self.speed_warning, self.torque_warning, self.power_warning])
                )

                self.content = self.custom_card
        except:
            logging.exception('exception occured at GeneralLimitationWarning.build')

    def reset(self):
        try:
            if self.page and self.page.session:
                s = self.page.session
                if self.torque_warning is not None:
                    self.torque_warning.label = s.get("lang.common.torque")

                if self.speed_warning is not None:
                    self.speed_warning.label = s.get("lang.common.speed")

                if self.power_warning is not None:
                    self.power_warning.label = s.get("lang.common.power")

                if self.custom_card is not None:
                    self.custom_card.set_title(s.get("lang.setting.warning_limitations"))
        except:
            logging.exception('exception occured at GeneralLimitationWarning.before_update')

    def update_unit(self, system_unit: int):
        try:
            if self.page:
                self.system_unit = system_unit
                torque_warning = gdata.configLimitation.torque_warning
                power_warning = gdata.configLimitation.power_warning
                if self.system_unit == 0:

                    if self.torque_warning is not None:
                        self.torque_warning.suffix_text = "kNm"
                        self.torque_warning.value = round(torque_warning / 1000)

                    if self.power_warning is not None:
                        self.power_warning.suffix_text = "kW"
                        self.power_warning.value = round(power_warning / 1000)

                elif self.system_unit == 1:
                    if self.torque_warning is not None:
                        self.torque_warning.suffix_text = "Tm"
                        self.torque_warning.value = UnitConverter.nm_to_tm(torque_warning)

                    if self.power_warning is not None:
                        self.power_warning.suffix_text = "sHp"
                        self.power_warning.value = UnitConverter.w_to_shp(power_warning)

                if self.content and self.content.page:
                    self.content.update()
        except:
            logging.exception('exception occured at GeneralLimitationWarning.update_unit')

    def save_data(self, user_id: int):
        warning_speed = float(self.speed_warning.value)
        warning_torque = int(self.torque_warning.value)
        warning_power = int(self.power_warning.value)

        if self.system_unit == 0:
            # kNm to Nm
            warning_torque = UnitConverter.knm_to_nm(warning_torque)
            # kw to w
            warning_power = UnitConverter.kw_to_w(warning_power)
        elif self.system_unit == 1:
            # Tm to Nm
            warning_torque = UnitConverter.tm_to_nm(warning_torque)
            # shp to w
            warning_power = UnitConverter.shp_to_w(warning_power)

        Limitations.update(power_warning=warning_power, torque_warning=warning_torque, speed_warning=warning_speed).execute()
        gdata.configLimitation.set_default_value()

    def did_mount(self):
        self.update_unit(self.system_unit)

    def before_update(self):
        s = self.page.session
        # 文本框标题（label）
        self.torque_warning.label = s.get("lang.common.torque")
        self.speed_warning.label = s.get("lang.common.speed")
        self.power_warning.label = s.get("lang.common.power")
        # 卡片标题
        self.custom_card.heading = s.get("lang.setting.warning_limitations")
