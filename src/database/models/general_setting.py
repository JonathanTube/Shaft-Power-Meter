from peewee import FloatField
from src.database.base import BaseModel


class GeneralSetting(BaseModel):
    bearing_outer_diameter_D = FloatField(
        help_text="轴承外径D(mm)",
        verbose_name="Bearing outer diameter D (mm)"
    )
    bearing_inner_diameter_d = FloatField(
        help_text="轴承内径d(mm)",
        verbose_name="Bearing inner diameter d (mm)"
    )
    shaft_outer_radius_R = FloatField(
        help_text="轴外半径R(mm)",
        verbose_name="Shaft outer radius R (mm)"
    )
    shaft_inner_radius_r = FloatField(
        help_text="轴内半径r(mm)",
        verbose_name="Shaft inner radius r (mm)"
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

    torque_coefficient = FloatField(
        help_text="扭矩系数",
        verbose_name="Torque coefficient"
    )
    tension_compression_coefficient = FloatField(
        help_text="拉压系数",
        verbose_name="Tension-compression coefficient"
    )

    class Meta:
        table_name = 'general_setting'
