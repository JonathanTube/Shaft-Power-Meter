from peewee import FloatField
from ..base import BaseModel


class OfflineDefaultValue(BaseModel):
    torque_default_value = FloatField(verbose_name="扭矩默认值 (Nm)")

    thrust_default_value = FloatField(verbose_name="推力默认值 (N)")

    speed_default_value = FloatField(verbose_name="速度默认值 (RPM)")

    class Meta:
        table_name = 'offline_default_value'
