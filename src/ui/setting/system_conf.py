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
            text="Save",
            width=120,
            height=40,
            on_click=self.__save_data
        )
        self.cancel_button = ft.OutlinedButton(
            text="Cancel",
            width=120,
            height=40,
            on_click=self.__cancel_data
        )

        self.content = ft.Column(
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
                                self.cancel_button
                            ])
                    ]
                )
            ])

    def __get_eexi_limited_power(self) -> tuple[float, str]:
        _eexi_limited_power = self.last_system_settings.eexi_limited_power
        if self.system_unit == 0:
            return (_eexi_limited_power / 1000, "kW")
        else:
            return (UnitConverter.w_to_hp(_eexi_limited_power), "hp")

    def __set_eexi_limited_power(self, e):
        _eexi_limited_power = float(e.control.value)
        if self.system_unit == 0:
            self.last_system_settings.eexi_limited_power = _eexi_limited_power * 1000
        else:
            self.last_system_settings.eexi_limited_power = UnitConverter.hp_to_w(
                _eexi_limited_power)

    def __create_settings_card(self):
        self.display_thrust = ft.Switch(
            col={"md": 6}, label="Display Thrust",
            label_position=ft.LabelPosition.LEFT,
            value=self.last_system_settings.display_thrust,
            on_change=lambda e: setattr(
                self.last_system_settings, 'display_thrust', e.control.value)
        )

        self.sha_po_li = ft.Switch(
            col={"md": 6}, label="ShaPoLi",
            label_position=ft.LabelPosition.LEFT,
            value=self.last_system_settings.sha_po_li,
            on_change=lambda e: setattr(
                self.last_system_settings, 'sha_po_li', e.control.value)
        )

        self.single_propeller = ft.Radio(value="1", label="Single")
        self.twins_propeller = ft.Radio(value="2", label="Twins")
        self.amount_of_propeller_radios = ft.RadioGroup(
            content=ft.Row([
                self.single_propeller,
                self.twins_propeller
            ]),
            value=self.last_system_settings.amount_of_propeller,
            on_change=lambda e: setattr(
                self.last_system_settings, 'amount_of_propeller', e.control.value)
        )

        eexi_limited_power_value, eexi_limited_power_unit = self.__get_eexi_limited_power()
        self.eexi_limited_power = ft.TextField(
            col={"md": 6},
            label="EEXI Limited Power",
            value=eexi_limited_power_value,
            suffix_text=eexi_limited_power_unit,
            on_change=self.__set_eexi_limited_power
        )

        self.amount_of_propeller_label = ft.Text(
            "Amount Of Propeller",
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
            'Settings',
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
            label="Ship Type",
            value=self.last_ship_info.ship_type,
            on_change=lambda e: setattr(
                self.last_ship_info, 'ship_type', e.control.value)
        )
        self.ship_name = ft.TextField(
            label="Ship Name",
            value=self.last_ship_info.ship_name,
            on_change=lambda e: setattr(
                self.last_ship_info, 'ship_name', e.control.value)
        )
        self.imo_number = ft.TextField(
            label="IMO Number",
            value=self.last_ship_info.imo_number,
            on_change=lambda e: setattr(
                self.last_ship_info, 'imo_number', e.control.value)
        )
        self.ship_size = ft.TextField(
            label="Ship Size",
            value=self.last_ship_info.ship_size,
            on_change=lambda e: setattr(
                self.last_ship_info, 'ship_size', e.control.value)
        )

        self.ship_info_card = CustomCard(
            'Ship Info',
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
            label="Shaft Outer Diameter(D)", suffix_text="mm",
            value=self.last_factor_conf.bearing_outer_diameter_D,
            on_change=lambda e: setattr(
                self.last_factor_conf, 'bearing_outer_diameter_D', e.control.value)
        )

        self.shaft_inner_diameter = ft.TextField(
            label="Shaft Inner Diameter(d)",
            suffix_text="mm",
            value=self.last_factor_conf.bearing_inner_diameter_d,
            on_change=lambda e: setattr(
                self.last_factor_conf, 'bearing_inner_diameter_d', e.control.value)
        )

        self.sensitivity_factor_k = ft.TextField(
            label="Sensitivity Factor(k)",
            value=self.last_factor_conf.sensitivity_factor_k,
            on_change=lambda e: setattr(
                self.last_factor_conf, 'sensitivity_factor_k', e.control.value)
        )

        self.elastic_modulus_E = ft.TextField(
            label="Elastic Modulus(E)",
            value=self.last_factor_conf.elastic_modulus_E,
            suffix_text="Gpa",
            on_change=lambda e: setattr(
                self.last_factor_conf, 'elastic_modulus_E', e.control.value)
        )

        self.poisson_ratio_mu = ft.TextField(
            label="Poisson's Ratio(μ)",
            value=self.last_factor_conf.poisson_ratio_mu,
            on_change=lambda e: setattr(
                self.last_factor_conf, 'poisson_ratio_mu', e.control.value)
        )

        self.factor_conf_card = CustomCard(
            'Factor Conf.',
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
        if float(self.last_system_settings.eexi_limited_power) > float(self.last_propeller_setting.shaft_power_of_mcr_operating_point):
            Toast.show_error(
                e.page, "EEXI Limited Power must be less than Shaft Power of MCR Operating Point"
            )
            return

        self.last_system_settings.save()
        self.last_ship_info.save()
        self.last_factor_conf.save()
        e.page.session.get("sha_po_li").switch()
        Toast.show_success(e.page)

    def __cancel_data(self, e):
        self.__load_data()

        self.display_thrust.value = self.last_system_settings.display_thrust
        self.sha_po_li.value = self.last_system_settings.sha_po_li
        self.amount_of_propeller_radios.value = self.last_system_settings.amount_of_propeller
        eexi_limited_power_value, eexi_limited_power_unit = self.__get_eexi_limited_power()
        self.eexi_limited_power.value = eexi_limited_power_value
        self.eexi_limited_power.suffix_text = eexi_limited_power_unit
        self.settings_card.update()

        self.ship_type.value = self.last_ship_info.ship_type
        self.ship_name.value = self.last_ship_info.ship_name
        self.imo_number.value = self.last_ship_info.imo_number
        self.ship_size.value = self.last_ship_info.ship_size
        self.ship_info_card.update()

        self.shaft_outer_diameter.value = self.last_factor_conf.bearing_outer_diameter_D
        self.shaft_inner_diameter.value = self.last_factor_conf.bearing_inner_diameter_d
        self.sensitivity_factor_k.value = self.last_factor_conf.sensitivity_factor_k
        self.elastic_modulus_E.value = self.last_factor_conf.elastic_modulus_E
        self.poisson_ratio_mu.value = self.last_factor_conf.poisson_ratio_mu
        self.factor_conf_card.update()

        Toast.show_success(e.page)

    def __load_config(self):
        self.system_unit = Preference.get().system_unit

    def __load_data(self):
        self.last_system_settings = SystemSettings.get()
        self.last_propeller_setting = PropellerSetting.get()
        self.last_ship_info = ShipInfo.get()
        self.last_factor_conf = FactorConf.get()

    def __set_language(self):
        session = self.page.session
        self.display_thrust.label = session.get("lang.setting.display_thrust")
        self.amount_of_propeller_label.value = session.get(
            "lang.setting.amount_of_propeller")
        self.single_propeller.label = session.get(
            "lang.setting.single_propeller")
        self.twins_propeller.label = session.get(
            "lang.setting.twins_propeller")
        self.sha_po_li.label = session.get("lang.setting.enable_sha_po_li")
        self.eexi_limited_power.label = session.get(
            "lang.setting.eexi_limited_power")

        self.ship_type.label = session.get("lang.setting.ship_type")
        self.ship_name.label = session.get("lang.setting.ship_name")
        self.imo_number.label = session.get("lang.setting.imo_number")
        self.ship_size.label = session.get("lang.setting.ship_size")

        self.shaft_outer_diameter.label = session.get(
            "lang.setting.bearing_outer_diameter_D")
        self.shaft_inner_diameter.label = session.get(
            "lang.setting.bearing_inner_diameter_d")
        self.sensitivity_factor_k.label = session.get(
            "lang.setting.sensitivity_factor_k")
        self.elastic_modulus_E.label = session.get(
            "lang.setting.elastic_modulus_E")
        self.poisson_ratio_mu.label = session.get(
            "lang.setting.poisson_ratio_mu")

        self.settings_card.set_title(session.get("lang.setting.setting"))
        self.ship_info_card.set_title(session.get("lang.setting.ship_info"))
        self.factor_conf_card.set_title(
            session.get("lang.setting.factor_conf"))

        self.save_button.text = session.get("lang.button.save")
        self.cancel_button.text = session.get("lang.button.cancel")

    def before_update(self):
        self.__set_language()

    def did_mount(self):
        self.__set_language()
