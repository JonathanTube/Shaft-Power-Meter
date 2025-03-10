import flet as ft

from src.database.models.factor_conf import FactorConf
from src.database.models.ship_info import ShipInfo
from src.database.models.system_settings import SystemSettings
from ..common.custom_card import create_card
from ..common.toast import Toast


class SystemConf:
    def __init__(self):
        self.system_conf = None

        self.last_system_settings = SystemSettings.select().order_by(SystemSettings.id.desc()).first()
        if self.last_system_settings is None:
            self.last_system_settings = SystemSettings.create(running_mode=0, master_slave=0, display_thrust=False,
                                                              amount_of_propeller=1, sha_po_li=False)

        self.last_ship_info = ShipInfo.select().order_by(ShipInfo.id.desc()).first()
        if self.last_ship_info is None:
            self.last_ship_info = ShipInfo.create(ship_type="", ship_name="", imo_number="", ship_size="")

        # self.last_factory
        self.last_factor_conf = FactorConf.select().order_by(FactorConf.id.desc()).first()
        if self.last_factor_conf is None:
            self.last_factor_conf = FactorConf.create(bearing_outer_diameter_D=0,
                                                      bearing_inner_diameter_d=0,
                                                      sensitivity_factor_k=0,
                                                      elastic_modulus_E=0,
                                                      poisson_ratio_mu=0)

    def __set_system_settings(self, name, value):
        if name == 'running_mode':
            self.last_system_settings.running_mode = value
        elif name == 'amount_of_propeller':
            self.last_system_settings.amount_of_propeller = value
        elif name == 'display_thrust':
            self.last_system_settings.display_thrust = value
        elif name == 'sha_po_li':
            self.last_system_settings.sha_po_li = value

    def __create_settings_card(self):
        # ft.Row(
        #     col={"md": 6},
        #     controls=[
        #         ft.Text("Running Mode", width=140,
        #                 text_align=ft.TextAlign.RIGHT),
        #         ft.RadioGroup(content=ft.Row([
        #             ft.Radio(value="0", label="Master"),
        #             ft.Radio(value="1", label="Slave")]),
        #             value=self.last_system_settings.running_mode,
        #             on_change=lambda e: self.__set_system_settings('running_mode', e.control.value)
        #         )
        #     ]
        # ),
        self.display_thrust = ft.Switch(
            col={"md": 4}, label="Display Thrust",
            label_position=ft.LabelPosition.LEFT,
            value=self.last_system_settings.display_thrust,
            on_change=lambda e: self.__set_system_settings('display_thrust', e.control.value)
        )

        self.sha_po_li = ft.Switch(
            col={"md": 4}, label="ShaPoLi",
            label_position=ft.LabelPosition.LEFT,
            value=self.last_system_settings.sha_po_li,
            on_change=lambda e: self.__set_system_settings('sha_po_li', e.control.value)
        )

        self.amount_of_propeller = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="0", label="Single"), ft.Radio(value="1", label="Dual")
            ]),
            value=self.last_system_settings.amount_of_propeller,
            on_change=lambda e: self.__set_system_settings('amount_of_propeller', e.control.value)
        )

        self.settings_card = create_card(
            'Settings',
            col={'xs': 12},
            expand=True,
            body=ft.ResponsiveRow(
                controls=[
                    self.display_thrust,
                    self.sha_po_li,
                    ft.Row(
                        col={"md": 4},
                        controls=[
                            ft.Text("Amount Of Propeller", width=140, text_align=ft.TextAlign.RIGHT),
                            self.amount_of_propeller
                        ]
                    )
                ]
            )
        )

    def __set_ship_info(self, name, value):
        if name == 'ship_type':
            self.last_ship_info.ship_type = value
        elif name == 'ship_name':
            self.last_ship_info.ship_name = value
        elif name == 'imo_number':
            self.last_ship_info.imo_number = value
        elif name == 'ship_size':
            self.last_ship_info.ship_size = value

    def __create_ship_info_card(self):
        self.ship_type = ft.TextField(
            label="Ship Type",
            value=self.last_ship_info.ship_type,
            on_change=lambda e: self.__set_ship_info('ship_type', e.control.value)
        )
        self.ship_name = ft.TextField(
            label="Ship Name",
            value=self.last_ship_info.ship_name,
            on_change=lambda e: self.__set_ship_info('ship_name', e.control.value)
        )
        self.imo_number = ft.TextField(
            label="IMO Number",
            value=self.last_ship_info.imo_number,
            on_change=lambda e: self.__set_ship_info('imo_number', e.control.value)
        )
        self.ship_size = ft.TextField(
            label="Ship Size",
            value=self.last_ship_info.ship_size,
            on_change=lambda e: self.__set_ship_info('ship_size', e.control.value)
        )

        self.ship_info_card = create_card(
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

    def __set_factor_conf(self, name, value):
        if name == 'bearing_outer_diameter_D':
            self.last_factor_conf.bearing_outer_diameter_D = value
        elif name == 'bearing_inner_diameter_d':
            self.last_factor_conf.bearing_inner_diameter_d = value
        elif name == 'sensitivity_factor_k':
            self.last_factor_conf.sensitivity_factor_k = value
        elif name == 'elastic_modulus_E':
            self.last_factor_conf.elastic_modulus_E = value
        elif name == 'poisson_ratio_mu':
            self.last_factor_conf.poisson_ratio_mu = value

    def __create_factor_conf_card(self):
        self.shaft_outer_diameter = ft.TextField(
            label="Shaft Outer Diameter(D)", suffix_text="mm",
            value=self.last_factor_conf.bearing_outer_diameter_D,
            on_change=lambda e: self.__set_factor_conf('bearing_outer_diameter_D', e.control.value)
        )

        self.shaft_inner_diameter = ft.TextField(
            label="Shaft Inner Diameter(d)",
            suffix_text="mm",
            value=self.last_factor_conf.bearing_inner_diameter_d,
            on_change=lambda e: self.__set_factor_conf('bearing_inner_diameter_d', e.control.value)
        )

        self.sensitivity_factor_k = ft.TextField(
            label="Sensitivity Factor(k)",
            value=self.last_factor_conf.sensitivity_factor_k,
            on_change=lambda e: self.__set_factor_conf('sensitivity_factor_k', e.control.value)
        )

        self.elastic_modulus_E = ft.TextField(
            label="Elastic Modulus(E)",
            value=self.last_factor_conf.elastic_modulus_E,
            suffix_text="Gpa",
            on_change=lambda e: self.__set_factor_conf('elastic_modulus_E', e.control.value)
        )

        self.poisson_ratio_mu = ft.TextField(
            label="Poisson's Ratio(μ)",
            value=self.last_factor_conf.poisson_ratio_mu,
            on_change=lambda e: self.__set_factor_conf('poisson_ratio_mu', e.control.value)
        )

        self.factor_conf_card = create_card(
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
        self.last_system_settings.save()
        self.last_ship_info.save()
        self.last_factor_conf.save()
        Toast.show_success(e.page, message="保存成功")

    def __cancel_data(self, e):
        self.last_system_settings = SystemSettings.select().order_by(SystemSettings.id.desc()).first()
        self.last_ship_info = ShipInfo.select().order_by(ShipInfo.id.desc()).first()
        self.last_factor_conf = FactorConf.select().order_by(FactorConf.id.desc()).first()

        self.display_thrust.value = self.last_system_settings.display_thrust
        self.sha_po_li.value = self.last_system_settings.sha_po_li
        self.amount_of_propeller.value = self.last_system_settings.amount_of_propeller
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

        Toast.show_success(e.page, message="已取消")

    def create(self):
        self.__create_settings_card(),
        self.__create_ship_info_card(),
        self.__create_factor_conf_card(),
        self.system_conf = ft.Column(
            expand=True,
            controls=[
                ft.ResponsiveRow(
                    # expand=True,
                    alignment=ft.MainAxisAlignment.START,
                    controls=[
                        self.settings_card,
                        self.ship_info_card,
                        self.factor_conf_card,
                        ft.Row(
                            # expand=True,
                            col={'xs': 12},
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.FilledButton(text="Save", width=120, height=40, on_click=self.__save_data),
                                ft.OutlinedButton(text="Cancel", width=120, height=40, on_click=self.__cancel_data)
                            ])
                    ]
                )
            ])

        return self.system_conf
