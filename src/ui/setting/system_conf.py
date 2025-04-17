import subprocess
import sys
import flet as ft

from db.models.factor_conf import FactorConf
from db.models.preference import Preference
from db.models.propeller_setting import PropellerSetting
from db.models.ship_info import ShipInfo
from db.models.system_settings import SystemSettings
from ui.common.custom_card import CustomCard
from ui.common.toast import Toast
from utils.unit_converter import UnitConverter


class SystemConf(ft.Container):
    def __init__(self):
        super().__init__()
        self.__load_config()
        self.__load_data()

    def build(self):
        self.__create_settings_card()
        self.__create_ship_info_card()
        self.__create_factor_conf_card()

        self.save_button = ft.FilledButton(
            self.page.session.get("lang.button.save"),
            width=120,
            height=40,
            on_click=self.__save_data
        )
        self.reset_button = ft.OutlinedButton(
            self.page.session.get("lang.button.reset"),
            width=120,
            height=40,
            on_click=self.__reset_data
        )

        self.content = ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            controls=[
                ft.ResponsiveRow(
                    alignment=ft.MainAxisAlignment.START,
                    controls=[
                        self.settings_card,
                        self.ship_info_card,
                        self.factor_conf_card,
                        ft.Row(
                            col={'xs': 12},
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                self.save_button,
                                self.reset_button
                            ])
                    ]
                )
            ])

    def __get_eexi_limited_power(self) -> tuple[float, str]:
        _eexi_limited_power = self.system_settings.eexi_limited_power
        if self.system_unit == 0:
            return (_eexi_limited_power / 1000, "kW")
        else:
            return (UnitConverter.w_to_shp(_eexi_limited_power), "hp")

    def __set_eexi_limited_power(self, e):
        _eexi_limited_power = float(e.control.value)
        if self.system_unit == 0:
            self.system_settings.eexi_limited_power = _eexi_limited_power * 1000
        else:
            self.system_settings.eexi_limited_power = UnitConverter.shp_to_w(
                _eexi_limited_power)

    def __create_settings_card(self):
        self.display_thrust = ft.Switch(
            col={"md": 6}, label=self.page.session.get("lang.setting.display_thrust"), 
            label_position=ft.LabelPosition.LEFT,
            value=self.system_settings.display_thrust,
            on_change=lambda e: setattr(
                self.system_settings, 'display_thrust', e.control.value)
        )

        self.sha_po_li = ft.Switch(
            col={"md": 6}, label=self.page.session.get("lang.setting.enable_sha_po_li"),
            label_position=ft.LabelPosition.LEFT,
            value=self.system_settings.sha_po_li,
            on_change=lambda e: setattr(
                self.system_settings, 'sha_po_li', e.control.value)
        )

        self.single_propeller = ft.Radio(value="1", label=self.page.session.get("lang.setting.single_propeller"))
        self.twins_propeller = ft.Radio(value="2", label=self.page.session.get("lang.setting.twins_propeller"))
        self.amount_of_propeller_radios = ft.RadioGroup(
            content=ft.Row([
                self.single_propeller,
                self.twins_propeller
            ]),
            value=self.system_settings.amount_of_propeller,
            on_change=lambda e: setattr(
                self.system_settings, 'amount_of_propeller', e.control.value)
        )

        eexi_limited_power_value, eexi_limited_power_unit = self.__get_eexi_limited_power()
        self.eexi_limited_power = ft.TextField(
            col={"md": 6},
            label=self.page.session.get("lang.setting.eexi_limited_power"),
            value=eexi_limited_power_value,
            suffix_text=eexi_limited_power_unit,
            visible=self.system_settings.sha_po_li,
            on_change=self.__set_eexi_limited_power
        )

        self.eexi_breach_checking_duration = ft.TextField(
            col={"md": 6},
            label=self.page.session.get("lang.setting.eexi_breach_checking_duration"),
            value=self.system_settings.eexi_breach_checking_duration,
            suffix_text="seconds",
            on_change=lambda e: setattr(self.system_settings, 'eexi_breach_checking_duration', int(e.control.value))
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

        self.settings_card = CustomCard(
            self.page.session.get("lang.setting.setting"),
            col={'xs': 12},
            expand=True,
            body=ft.ResponsiveRow(
                controls=[
                    self.display_thrust,
                    amount_of_propeller_row,
                    self.sha_po_li,
                    self.eexi_limited_power
                ]
            ))

    def __create_ship_info_card(self):
        self.ship_type = ft.TextField(
            label=self.page.session.get("lang.setting.ship_type"),
            value=self.ship_info.ship_type,
            on_change=lambda e: setattr(
                self.ship_info, 'ship_type', e.control.value)
        )
        self.ship_name = ft.TextField(
            label=self.page.session.get("lang.setting.ship_name"),
            value=self.ship_info.ship_name,
            on_change=lambda e: setattr(
                self.ship_info, 'ship_name', e.control.value)
        )
        self.imo_number = ft.TextField(
            label=self.page.session.get("lang.setting.imo_number"),
            value=self.ship_info.imo_number,
            on_change=lambda e: setattr(
                self.ship_info, 'imo_number', e.control.value)
        )
        self.ship_size = ft.TextField(
            label=self.page.session.get("lang.setting.ship_size"),
            value=self.ship_info.ship_size,
            on_change=lambda e: setattr(
                self.ship_info, 'ship_size', e.control.value)
        )

        self.ship_info_card = CustomCard(
            self.page.session.get("lang.setting.ship_info"),
            ft.Column(
                controls=[
                    self.ship_type,
                    self.ship_name,
                    self.imo_number,
                    self.ship_size
                ]
            ),
            height=360)

    def __create_factor_conf_card(self):
        self.shaft_outer_diameter = ft.TextField(
            label=self.page.session.get("lang.setting.shaft_outer_diameter_D"), suffix_text="mm",
            value=self.factor_conf.bearing_outer_diameter_D,
            on_change=lambda e: setattr(
                self.factor_conf, 'bearing_outer_diameter_D', e.control.value)
        )

        self.shaft_inner_diameter = ft.TextField(
            label=self.page.session.get("lang.setting.shaft_inner_diameter_d"),
            suffix_text="mm",
            value=self.factor_conf.bearing_inner_diameter_d,
            on_change=lambda e: setattr(
                self.factor_conf, 'bearing_inner_diameter_d', e.control.value)
        )

        self.sensitivity_factor_k = ft.TextField(
            label=self.page.session.get("lang.setting.sensitivity_factor_k"),
            value=self.factor_conf.sensitivity_factor_k,
            on_change=lambda e: setattr(
                self.factor_conf, 'sensitivity_factor_k', e.control.value)
        )

        self.elastic_modulus_E = ft.TextField(
            label=self.page.session.get("lang.setting.elastic_modulus_E"),
            value=self.factor_conf.elastic_modulus_E,
            suffix_text="Gpa",
            on_change=lambda e: setattr(
                self.factor_conf, 'elastic_modulus_E', e.control.value)
        )

        self.poisson_ratio_mu = ft.TextField(
            label=self.page.session.get("lang.setting.poisson_ratio_mu"),
            value=self.factor_conf.poisson_ratio_mu,
            on_change=lambda e: setattr(
                self.factor_conf, 'poisson_ratio_mu', e.control.value)
        )

        self.factor_conf_card = CustomCard(
            self.page.session.get("lang.setting.factor_conf"),
            ft.Column(
                controls=[
                    self.shaft_outer_diameter,
                    self.shaft_inner_diameter,
                    self.sensitivity_factor_k,
                    self.elastic_modulus_E,
                    self.poisson_ratio_mu
                ]
            ),
            height=360
        )

    def __save_data(self, e):
        self.system_settings.save()

        if self.system_settings.sha_po_li:
            self.eexi_limited_power.visible = True
            self.page.session.set(
                "eexi_limited_power",
                self.system_settings.eexi_limited_power
            )
        else:
            self.eexi_limited_power.visible = False
            self.page.session.set("eexi_limited_power", None)

        self.ship_info.save()
        self.factor_conf.save()

        dlg = ft.AlertDialog(
            title=ft.Text(self.page.session.get("lang.setting.test_mode.please_confirm")),    
            content=ft.Text(self.page.session.get("lang.setting.test_mode.system_restart_after_change")),
            actions=[ft.TextButton(self.page.session.get("lang.button.confirm"), on_click=self.on_restart_app)]
        )
        self.page.open(dlg)

    async def restart_app(self):
        exe = sys.executable
        args = [exe] + sys.argv
        subprocess.Popen(args)
        sys.exit(0)

    def on_restart_app(self, e):
        self.page.run_task(self.restart_app)

    def __reset_data(self, e):
        self.__load_data()
        self.content.clean()
        self.build()
        Toast.show_success(e.page)

    def __load_config(self):
        self.system_unit = Preference.get().system_unit

    def __load_data(self):
        self.system_settings = SystemSettings.get()
        self.propeller_setting = PropellerSetting.get()
        self.ship_info = ShipInfo.get()
        self.factor_conf = FactorConf.get()