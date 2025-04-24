import flet as ft
from db.models.opearation_log import OperationLog
from db.models.preference import Preference
from db.models.system_settings import SystemSettings
from ui.common.custom_card import CustomCard
from utils.unit_converter import UnitConverter
from ui.common.keyboard import keyboard
from common.operation_type import OperationType
from common.global_data import gdata
from playhouse.shortcuts import model_to_dict
from common.control_manager import ControlManager


class SystemConfSettings(CustomCard):
    def __init__(self):
        super().__init__()
        self.system_settings: SystemSettings = SystemSettings.get()
        self.preference: Preference = Preference.get()

    def build(self):
        self.display_thrust = ft.Switch(
            col={"md": 6}, label=self.page.session.get("lang.setting.display_thrust"),
            label_position=ft.LabelPosition.LEFT,
            value=self.system_settings.display_thrust
        )

        self.sha_po_li = ft.Switch(
            col={"md": 6}, label=self.page.session.get("lang.setting.enable_sha_po_li"),
            label_position=ft.LabelPosition.LEFT,
            value=self.system_settings.sha_po_li,
            on_change=self.__on_sha_po_li_change
        )

        self.display_propeller_curve = ft.Switch(
            col={"md": 6}, label=self.page.session.get("lang.setting.display_propeller_curve"),
            label_position=ft.LabelPosition.LEFT,
            value=self.system_settings.display_propeller_curve
        )

        self.single_propeller = ft.Radio(value="1", label=self.page.session.get("lang.setting.single_propeller"))
        self.twins_propeller = ft.Radio(value="2", label=self.page.session.get("lang.setting.twins_propeller"))
        self.amount_of_propeller_radios = ft.RadioGroup(
            content=ft.Row([self.single_propeller, self.twins_propeller]),
            value=self.system_settings.amount_of_propeller
        )

        eexi_limited_power_value, eexi_limited_power_unit = self.__get_eexi_limited_power()

        self.eexi_limited_power = ft.TextField(
            col={"md": 6},
            label=self.page.session.get("lang.setting.eexi_limited_power"),
            value=eexi_limited_power_value,
            suffix_text=eexi_limited_power_unit,
            visible=self.system_settings.sha_po_li,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'float')
        )

        self.eexi_breach_checking_duration = ft.TextField(
            col={"md": 6},
            label=self.page.session.get("lang.setting.eexi_breach_checking_duration"),
            value=self.system_settings.eexi_breach_checking_duration,
            suffix_text="seconds",
            visible=self.system_settings.sha_po_li,
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control, 'int')
        )

        self.amount_of_propeller_label = ft.Text(
            self.page.session.get("lang.setting.amount_of_propeller"),
            text_align=ft.TextAlign.RIGHT
        )

        amount_of_propeller_row = ft.Row(
            col={"md": 6},
            controls=[
                self.amount_of_propeller_label,
                self.amount_of_propeller_radios
            ]
        )

        self.heading = self.page.session.get("lang.setting.setting")
        self.col = {'xs': 12}
        self.expand = True
        self.body = ft.ResponsiveRow(
            controls=[
                amount_of_propeller_row,
                self.display_thrust,
                self.sha_po_li,
                self.display_propeller_curve,
                self.eexi_limited_power,
                self.eexi_breach_checking_duration
            ]
        )
        super().build()

    def __on_sha_po_li_change(self, e):
        if self.system_settings.sha_po_li:
            self.eexi_limited_power.visible = True
            self.eexi_breach_checking_duration.visible = True
        else:
            self.eexi_limited_power.visible = False
            self.eexi_breach_checking_duration.visible = False
        self.eexi_limited_power.update()
        self.eexi_breach_checking_duration.update()

    def __get_eexi_limited_power(self) -> tuple[float, str]:
        _eexi_limited_power = self.system_settings.eexi_limited_power
        if self.preference.system_unit == 0:
            return (_eexi_limited_power / 1000, "kW")
        else:
            return (UnitConverter.w_to_shp(_eexi_limited_power), "hp")

    def save(self, user_id: int):
        self.system_settings.amount_of_propeller = self.amount_of_propeller_radios.value
        self.system_settings.display_thrust = self.display_thrust.value
        self.system_settings.sha_po_li = self.sha_po_li.value
        self.system_settings.display_propeller_curve = self.display_propeller_curve.value

        unit = self.preference.system_unit
        if unit == 0:
            self.system_settings.eexi_limited_power = self.eexi_limited_power.value * 1000
        else:
            self.system_settings.eexi_limited_power = UnitConverter.shp_to_w(self.eexi_limited_power.value)

        self.system_settings.eexi_breach_checking_duration = self.eexi_breach_checking_duration.value

        self.system_settings.save()

        gdata.display_propeller_curve = self.display_propeller_curve.value
        if ControlManager.zero_cal is not None:
            ControlManager.zero_cal.visible = self.display_propeller_curve.value
            ControlManager.zero_cal.update()

        OperationLog.create(
            user_id=user_id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.SYSTEM_CONF_SETTING,
            operation_content=model_to_dict(self.system_settings)
        )
