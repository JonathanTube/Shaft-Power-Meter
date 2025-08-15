import logging
import flet as ft
from db.models.user import User
from ui.common.custom_card import CustomCard
from utils.unit_converter import UnitConverter
from db.models.system_settings import SystemSettings
from ui.common.keyboard import keyboard
from common.global_data import gdata
from common.global_data import gdata


class SystemConfSettings(ft.Container):
    def build(self):
        try:
            if self.page and self.page.session:
                self.mode_master = ft.Radio(
                    value='master',
                    label=self.page.session.get("lang.setting.master")
                )
                self.mode_slave = ft.Radio(
                    value='slave',
                    label=self.page.session.get("lang.setting.slave")
                )
                self.running_mode = ft.RadioGroup(
                    content=ft.Row([self.mode_master, self.mode_slave]),
                    value='master' if gdata.configCommon.is_master else 'slave',
                    on_change=self.__on_running_mode_change
                )

                self.running_mode_row = ft.Row(
                    col={"md": 6},
                    controls=[
                        ft.Text(
                            self.page.session.get("lang.setting.running_mode"),
                            text_align=ft.TextAlign.RIGHT
                        ),
                        self.running_mode
                    ]
                )

                self.is_individual = ft.Checkbox(
                    col={"md": 6}, label=self.page.session.get("lang.setting.is_individual"),
                    visible=gdata.configCommon.is_master,
                    value=gdata.configCommon.is_individual
                )

                self.enable_gps = ft.Checkbox(
                    col={"md": 6}, label=self.page.session.get("lang.setting.enable_gps"),
                    visible=gdata.configCommon.is_master,
                    value=gdata.configCommon.enable_gps
                )

                self.display_thrust = ft.Checkbox(
                    col={"md": 6}, label=self.page.session.get("lang.setting.display_thrust"),
                    value=gdata.configCommon.show_thrust
                )

                self.sha_po_li = ft.Checkbox(
                    col={"md": 6}, label=self.page.session.get("lang.setting.enable_sha_po_li"),
                    value=gdata.configCommon.shapoli
                )

                self.display_propeller_curve = ft.Checkbox(
                    col={"md": 6}, label=self.page.session.get("lang.setting.display_propeller_curve"),
                    value=gdata.configCommon.show_propeller_curve
                )

                unlimited_power_value, unlimited_power_unit = self.__get_unlimited_power()
                self.unlimited_power = ft.TextField(
                    col={"md": 6},
                    label=self.page.session.get("lang.setting.unlimited_power"),
                    value=unlimited_power_value,
                    suffix_text=unlimited_power_unit,
                    visible=gdata.configCommon.shapoli,
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, 'int')
                )

                eexi_limited_power_value, eexi_limited_power_unit = self.__get_eexi_limited_power()
                self.eexi_limited_power = ft.TextField(
                    col={"md": 6},
                    label=self.page.session.get("lang.setting.eexi_limited_power"),
                    value=eexi_limited_power_value,
                    suffix_text=eexi_limited_power_unit,
                    visible=gdata.configCommon.shapoli,
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, 'int')
                )

                self.eexi_breach_checking_duration = ft.TextField(
                    col={"md": 6},
                    label=self.page.session.get("lang.setting.eexi_breach_checking_duration"),
                    value=gdata.configCommon.eexi_breach_checking_duration,
                    suffix_text="seconds",
                    visible=gdata.configCommon.shapoli,
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, 'int')
                )

                self.chk_hide_admin_account = ft.Checkbox(
                    col={"md": 6}, label=self.page.session.get("lang.setting.hide_admin_account"),
                    value=gdata.configCommon.hide_admin_account
                )

                self.single_propeller = ft.Radio(value="1", label=self.page.session.get("lang.setting.single_propeller"))
                self.twins_propeller = ft.Radio(value="2", label=self.page.session.get("lang.setting.twins_propeller"))
                self.amount_of_propeller_radios = ft.RadioGroup(
                    content=ft.Row([self.single_propeller, self.twins_propeller]),
                    value=gdata.configCommon.amount_of_propeller
                )
                self.amount_of_propeller_row = ft.Row(
                    col={"md": 6},
                    visible=False,
                    controls=[
                        ft.Text(
                            self.page.session.get("lang.setting.amount_of_propeller"),
                            text_align=ft.TextAlign.RIGHT
                        ),
                        self.amount_of_propeller_radios
                    ]
                )

                self.custom_card = CustomCard(
                    self.page.session.get("lang.setting.setting"),
                    ft.ResponsiveRow(controls=[
                        self.running_mode_row,
                        self.enable_gps,
                        self.is_individual,
                        self.display_thrust,
                        self.amount_of_propeller_row,
                        self.display_propeller_curve,
                        self.sha_po_li,
                        self.chk_hide_admin_account,
                        self.unlimited_power,
                        self.eexi_limited_power,
                        self.eexi_breach_checking_duration
                    ]),
                    col={"xs": 12})
                self.content = self.custom_card
        except:
            logging.exception('exception occured at SystemConfSettings.build')

    def __on_running_mode_change(self, e):
        if self.is_individual and self.is_individual.page:
            self.is_individual.visible = e.data == 'master'
            self.is_individual.value = e.data == 'slave'
            self.is_individual.update()

        if self.enable_gps and self.enable_gps.page:
            self.enable_gps.visible = e.data == 'master'
            self.enable_gps.value = False
            self.enable_gps.update()

    def __get_unlimited_power(self) -> tuple[int, str]:
        _unlimited_power = gdata.configCommon.unlimited_power
        if gdata.configPreference.system_unit == 0:
            return (round(_unlimited_power / 1000), "kW")
        else:
            return (UnitConverter.w_to_shp(_unlimited_power), "sHp")

    def __get_eexi_limited_power(self) -> tuple[int, str]:
        _eexi_limited_power = gdata.configCommon.eexi_limited_power
        if gdata.configPreference.system_unit == 0:
            return (round(_eexi_limited_power / 1000), "kW")
        else:
            return (UnitConverter.w_to_shp(_eexi_limited_power), "sHp")

    def save(self, user: User):
        # 不要处理异常，外部已经catch
        if self.page is None or self.page.session is None:
            return

        is_master = True if self.running_mode.value == 'master' else False
        is_individual = self.is_individual.value
        enable_gps = self.enable_gps.value
        amount_of_propeller = self.amount_of_propeller_radios.value
        display_thrust = self.display_thrust.value
        sha_po_li = self.sha_po_li.value
        display_propeller_curve = self.display_propeller_curve.value
        hide_admin_account = self.chk_hide_admin_account.value

        SystemSettings.update(
            is_master=is_master, is_individual=is_individual, enable_gps=enable_gps, amount_of_propeller=amount_of_propeller,
            display_thrust=display_thrust, sha_po_li=sha_po_li, display_propeller_curve=display_propeller_curve, hide_admin_account=hide_admin_account
        ).execute()

        unit = gdata.configPreference.system_unit
        eexi_breach_checking_duration = self.eexi_breach_checking_duration.value

        unlimited_power = 0
        eexi_limited_power = 0
        if unit == 0:
            unlimited_power = int(self.unlimited_power.value) * 1000
            eexi_limited_power = int(self.eexi_limited_power.value) * 1000
        else:
            unlimited_power = UnitConverter.shp_to_w(self.unlimited_power.value)
            eexi_limited_power = UnitConverter.shp_to_w(self.eexi_limited_power.value)

        SystemSettings.update(
            eexi_breach_checking_duration=eexi_breach_checking_duration,
            unlimited_power=unlimited_power, eexi_limited_power=eexi_limited_power
        ).execute()
        gdata.configCommon.set_default_value()

    def before_update(self):
        try:
            self.unlimited_power.visible = gdata.configCommon.shapoli
            self.eexi_limited_power.visible = gdata.configCommon.shapoli
            self.eexi_breach_checking_duration.visible = gdata.configCommon.shapoli
            self.enable_gps.visible = gdata.configCommon.is_master
        except:
            logging.exception('exception occured at SystemConfSettings.before_update')
