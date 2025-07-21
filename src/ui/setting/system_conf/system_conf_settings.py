import logging
import flet as ft
from db.models.operation_log import OperationLog
from db.models.preference import Preference
from db.models.system_settings import SystemSettings
from db.models.user import User
from ui.common.custom_card import CustomCard
from utils.unit_converter import UnitConverter
from common.operation_type import OperationType
from playhouse.shortcuts import model_to_dict
from ui.common.keyboard import keyboard
from common.global_data import gdata
from common.global_data import gdata


class SystemConfSettings(ft.Container):
    def __init__(self):
        super().__init__()
        self.system_settings: SystemSettings = SystemSettings.get()
        self.preference: Preference = Preference.get()

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
                    value='master' if self.system_settings.is_master else 'slave',
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
                    visible=self.system_settings.is_master,
                    value=self.system_settings.is_individual
                )

                self.enable_gps = ft.Checkbox(
                    col={"md": 6}, label=self.page.session.get("lang.setting.enable_gps"),
                    value=self.system_settings.enable_gps
                )

                self.display_thrust = ft.Checkbox(
                    col={"md": 6}, label=self.page.session.get("lang.setting.display_thrust"),
                    value=self.system_settings.display_thrust
                )

                self.sha_po_li = ft.Checkbox(
                    col={"md": 6}, label=self.page.session.get("lang.setting.enable_sha_po_li"),
                    value=self.system_settings.sha_po_li,
                    on_change=self.__on_sha_po_li_change
                )

                self.display_propeller_curve = ft.Checkbox(
                    col={"md": 6}, label=self.page.session.get("lang.setting.display_propeller_curve"),
                    value=self.system_settings.display_propeller_curve
                )

                eexi_limited_power_value, eexi_limited_power_unit = self.__get_eexi_limited_power()
                self.eexi_limited_power = ft.TextField(
                    col={"md": 6},
                    label=self.page.session.get("lang.setting.eexi_limited_power"),
                    value=eexi_limited_power_value,
                    suffix_text=eexi_limited_power_unit,
                    visible=self.system_settings.sha_po_li,
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, 'float')
                )

                self.eexi_breach_checking_duration = ft.TextField(
                    col={"md": 6},
                    label=self.page.session.get("lang.setting.eexi_breach_checking_duration"),
                    value=self.system_settings.eexi_breach_checking_duration,
                    suffix_text="seconds",
                    visible=self.system_settings.sha_po_li,
                    read_only=True,
                    can_request_focus=False,
                    on_click=lambda e: keyboard.open(e.control, 'int')
                )

                self.chk_hide_admin_account = ft.Checkbox(
                    col={"md": 6}, label=self.page.session.get("lang.setting.hide_admin_account"),
                    value=self.system_settings.hide_admin_account
                )

                self.single_propeller = ft.Radio(value="1", label=self.page.session.get("lang.setting.single_propeller"))
                self.twins_propeller = ft.Radio(value="2", label=self.page.session.get("lang.setting.twins_propeller"))
                self.amount_of_propeller_radios = ft.RadioGroup(
                    content=ft.Row([self.single_propeller, self.twins_propeller]),
                    value=self.system_settings.amount_of_propeller
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
                        self.eexi_limited_power,
                        self.eexi_breach_checking_duration
                    ]),
                    col={"xs": 12})
                self.content = self.custom_card
        except:
            logging.exception('exception occured at SystemConfSettings.build')

    def __on_running_mode_change(self, e):
        self.is_individual.visible = e.data == 'master'
        self.is_individual.value = e.data == 'slave'
        self.is_individual.update()

        self.enable_gps.value = False
        self.enable_gps.update()

    def __on_sha_po_li_change(self, e):
        try:
            if self.system_settings.sha_po_li:
                self.eexi_limited_power.visible = True
                self.eexi_breach_checking_duration.visible = True
            else:
                self.eexi_limited_power.visible = False
                self.eexi_breach_checking_duration.visible = False
            self.eexi_limited_power.update()
            self.eexi_breach_checking_duration.update()
        except:
            logging.exception('exception occured at SystemConfSettings.__on_sha_po_li_change')

    def __get_eexi_limited_power(self) -> tuple[float, str]:
        _eexi_limited_power = self.system_settings.eexi_limited_power
        if self.preference.system_unit == 0:
            return (_eexi_limited_power / 1000, "kW")
        else:
            return (UnitConverter.w_to_shp(_eexi_limited_power), "sHp")

    def save(self, user: User):
        # 不要处理异常，外部已经catch
        if self.page is None or self.page.session is None:
            return

        is_master_old = self.system_settings.is_master
        is_master_new = True if self.running_mode.value == 'master' else False
        self.system_settings.is_master = is_master_new

        is_individual_old = self.system_settings.is_individual
        is_individual_new = self.is_individual.value
        self.system_settings.is_individual = is_individual_new

        enable_gps_old = self.system_settings.enable_gps
        enable_gps_new = self.enable_gps.value
        self.system_settings.enable_gps = enable_gps_new

        # 如果运行模式被切换
        if is_master_new != is_master_old or is_individual_new != is_individual_old or enable_gps_new != enable_gps_old:
            self.system_settings.save()
            gdata.is_master = self.system_settings.is_master
            raise SystemError("running mode changed")


        self.system_settings.amount_of_propeller = self.amount_of_propeller_radios.value
        self.system_settings.display_thrust = self.display_thrust.value
        self.system_settings.sha_po_li = self.sha_po_li.value
        self.system_settings.display_propeller_curve = self.display_propeller_curve.value
        self.system_settings.hide_admin_account = self.chk_hide_admin_account.value

        unit = self.preference.system_unit
        if unit == 0:
            self.system_settings.eexi_limited_power = float(self.eexi_limited_power.value) * 1000
        else:
            self.system_settings.eexi_limited_power = UnitConverter.shp_to_w(float(self.eexi_limited_power.value))

        self.system_settings.eexi_breach_checking_duration = self.eexi_breach_checking_duration.value

        self.system_settings.save()

        gdata.is_master = self.system_settings.is_master

        gdata.amount_of_propeller = self.system_settings.amount_of_propeller

        gdata.shapoli = self.system_settings.sha_po_li

        gdata.eexi_breach_checking_duration = int(self.system_settings.eexi_breach_checking_duration)

        gdata.eexi_limited_power = float(self.system_settings.eexi_limited_power)

        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.SYSTEM_CONF_SETTING,
            operation_content=model_to_dict(self.system_settings)
        )