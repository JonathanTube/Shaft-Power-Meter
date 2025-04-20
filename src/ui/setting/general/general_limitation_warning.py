import flet as ft

from ui.common.custom_card import CustomCard
from db.models.limitations import Limitations
from utils.unit_converter import UnitConverter
reg_digital = r'^(\d+\.?\d*|)$'  # 允许整数、小数或空字符串


class GeneralLimitationWarning(ft.Container):
    def __init__(self, system_unit: int):
        super().__init__()
        self.expand = True
        self.col = {"md": 6}
        self.system_unit = system_unit
        self.limitations: Limitations = Limitations.get()

    def build(self):
        self.torque_warning = ft.TextField(suffix_text="kNm",
                                           label=self.page.session.get("lang.common.torque"),
                                           input_filter=ft.InputFilter(regex_string=reg_digital),
                                           value=self.limitations.torque_warning)

        self.speed_warning = ft.TextField(suffix_text="rpm",
                                          label=self.page.session.get("lang.common.speed"),
                                          input_filter=ft.InputFilter(regex_string=reg_digital),
                                          value=self.limitations.speed_warning)

        self.power_warning = ft.TextField(suffix_text="kW",
                                          label=self.page.session.get("lang.common.power"),
                                          input_filter=ft.InputFilter(regex_string=reg_digital),
                                          value=self.limitations.power_warning)

        self.content = CustomCard(
            self.page.session.get("lang.setting.warning_limitations"),
            ft.Column(controls=[self.speed_warning, self.torque_warning, self.power_warning])
        )

    def update_unit(self, system_unit: int):
        self.system_unit = system_unit
        torque_warning = self.limitations.torque_warning
        power_warning = self.limitations.power_warning
        if self.system_unit == 0:
            self.torque_warning.suffix_text = "kNm"
            self.torque_warning.value = round(torque_warning / 1000, 1)

            self.power_warning.suffix_text = "kW"
            self.power_warning.value = round(power_warning / 1000, 1)

        elif self.system_unit == 1:
            self.torque_warning.suffix_text = "Tm"
            self.torque_warning.value = UnitConverter.nm_to_tm(torque_warning)

            self.power_warning.suffix_text = "shp"
            self.power_warning.value = UnitConverter.w_to_shp(power_warning)

        self.content.update()

    def save_data(self):
        warning_speed = float(self.speed_warning.value or 0)
        warning_torque = float(self.torque_warning.value or 0)
        warning_power = float(self.power_warning.value or 0)

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

        Limitations.update(
            power_warning=warning_power,
            torque_warning=warning_torque,
            speed_warning=warning_speed
        ).where(Limitations.id == self.limitations.id).execute()

    def did_mount(self):
        self.update_unit(self.system_unit)
