import flet as ft
from db.models.factor_conf import FactorConf
from db.models.operation_log import OperationLog
from common.operation_type import OperationType
from playhouse.shortcuts import model_to_dict
from ui.common.custom_card import CustomCard
from common.global_data import gdata
from ui.common.keyboard import keyboard

class IOSettingFactor(CustomCard):
    def __init__(self):
        super().__init__()
        self.factor_conf = FactorConf.get()

    def build(self):
        self.shaft_outer_diameter = ft.TextField(
            label=self.page.session.get("lang.setting.bearing_outer_diameter_D"), suffix_text="mm",
            value=self.factor_conf.bearing_outer_diameter_D,
            col={'sm': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.shaft_inner_diameter = ft.TextField(
            label=self.page.session.get("lang.setting.bearing_inner_diameter_d"),
            suffix_text="mm",
            value=self.factor_conf.bearing_inner_diameter_d,
            col={'sm': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.sensitivity_factor_k = ft.TextField(
            label=self.page.session.get("lang.setting.sensitivity_factor_k"),
            value=self.factor_conf.sensitivity_factor_k,
            col={'sm': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.elastic_modulus_E = ft.TextField(
            label=self.page.session.get("lang.setting.elastic_modulus_E"),
            value=self.factor_conf.elastic_modulus_E,
            suffix_text="Gpa",
            col={'sm': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.poisson_ratio_mu = ft.TextField(
            label=self.page.session.get("lang.setting.poisson_ratio_mu"),
            value=self.factor_conf.poisson_ratio_mu,
            col={'sm': 6},
            read_only=True,
            on_focus=lambda e: keyboard.open(e.control)
        )

        self.heading = self.page.session.get("lang.setting.factor_conf")
        self.body = ft.ResponsiveRow(
            controls=[
                self.shaft_outer_diameter,
                self.shaft_inner_diameter,
                self.sensitivity_factor_k,
                self.elastic_modulus_E,
                self.poisson_ratio_mu
            ]
        )
        self.col = {"sm": 12}
        super().build()

    def save_data(self, user_id: int):
        self.factor_conf.bearing_outer_diameter_D = self.shaft_outer_diameter.value
        self.factor_conf.bearing_inner_diameter_d = self.shaft_inner_diameter.value
        self.factor_conf.sensitivity_factor_k = self.sensitivity_factor_k.value
        self.factor_conf.elastic_modulus_E = self.elastic_modulus_E.value
        self.factor_conf.poisson_ratio_mu = self.poisson_ratio_mu.value

        self.factor_conf.save()
        OperationLog.create(
            user_id=user_id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.IO_CONF_FACTOR,
            operation_content=model_to_dict(self.factor_conf)
        )
