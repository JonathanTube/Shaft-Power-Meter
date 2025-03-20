from peewee import FloatField
from ..base import BaseModel, db


class Limitations(BaseModel):
    speed_max = FloatField(verbose_name="最大转速")

    torque_max = FloatField(verbose_name="最大扭矩")

    power_max = FloatField(verbose_name="最大功率")

    speed_warning = FloatField(verbose_name="警告转速")

    torque_warning = FloatField(verbose_name="警告扭矩")

    power_warning = FloatField(verbose_name="警告功率")

    class Meta:
        table_name = 'limitations'
