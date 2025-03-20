from peewee import FloatField
from ..base import BaseModel, db


class FactorConf(BaseModel):
    bearing_outer_diameter_D = FloatField(
        help_text="轴承外径D(mm)",
        verbose_name="Bearing outer diameter D (mm)"
    )
    bearing_inner_diameter_d = FloatField(
        help_text="轴承内径d(mm)",
        verbose_name="Bearing inner diameter d (mm)"
    )
    elastic_modulus_E = FloatField(
        help_text="弹性模量E(Gpa)",
        verbose_name="Elastic modulus E (GPa)"
    )
    poisson_ratio_mu = FloatField(
        help_text="泊松比μ",
        verbose_name="Poisson's ratio μ"
    )
    sensitivity_factor_k = FloatField(
        help_text="灵敏度因子k",
        verbose_name="Sensitivity factor k"
    )

    class Meta:
        table_name = 'factor_conf'
