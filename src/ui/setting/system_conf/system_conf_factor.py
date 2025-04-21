import flet as ft
from db.models.factor_conf import FactorConf
from ui.common.custom_card import CustomCard


class SystemConfFactor(CustomCard):
    def __init__(self):
        super().__init__()
        self.factor_conf = FactorConf.get()

    def build(self):
        self.shaft_outer_diameter = ft.TextField(
            label=self.page.session.get("lang.setting.shaft_outer_diameter_D"), suffix_text="mm",
            value=self.factor_conf.bearing_outer_diameter_D
        )

        self.shaft_inner_diameter = ft.TextField(
            label=self.page.session.get("lang.setting.shaft_inner_diameter_d"),
            suffix_text="mm",
            value=self.factor_conf.bearing_inner_diameter_d
        )

        self.sensitivity_factor_k = ft.TextField(
            label=self.page.session.get("lang.setting.sensitivity_factor_k"),
            value=self.factor_conf.sensitivity_factor_k
        )

        self.elastic_modulus_E = ft.TextField(
            label=self.page.session.get("lang.setting.elastic_modulus_E"),
            value=self.factor_conf.elastic_modulus_E,
            suffix_text="Gpa"
        )

        self.poisson_ratio_mu = ft.TextField(
            label=self.page.session.get("lang.setting.poisson_ratio_mu"),
            value=self.factor_conf.poisson_ratio_mu
        )

        self.heading = self.page.session.get("lang.setting.factor_conf")
        self.body = ft.Column(
            controls=[
                self.shaft_outer_diameter,
                self.shaft_inner_diameter,
                self.sensitivity_factor_k,
                self.elastic_modulus_E,
                self.poisson_ratio_mu
            ]
        )
        self.height = 360
        super().build()

    def save(self):
        self.factor_conf.bearing_outer_diameter_D = self.shaft_outer_diameter.value
        self.factor_conf.bearing_inner_diameter_d = self.shaft_inner_diameter.value
        self.factor_conf.sensitivity_factor_k = self.sensitivity_factor_k.value
        self.factor_conf.elastic_modulus_E = self.elastic_modulus_E.value
        self.factor_conf.poisson_ratio_mu = self.poisson_ratio_mu.value
        self.factor_conf.save()
