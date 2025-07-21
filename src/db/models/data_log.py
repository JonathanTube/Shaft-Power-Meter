from peewee import FloatField, DateTimeField, CharField, BooleanField
from ..base import BaseModel


class DataLog(BaseModel):
    utc_date_time = DateTimeField(verbose_name="UTC日期时间")

    name = CharField(verbose_name="名称:sps or sps2")

    ad_0_torque = FloatField(verbose_name="扭矩(Nm)")

    ad_1_thrust = FloatField(verbose_name="推力(N)")

    speed = FloatField(verbose_name="转速(RPM)")

    power = FloatField(verbose_name="功率(W)")

    is_overload = BooleanField(verbose_name="是否过载", default=False)

    class Meta:
        table_name = 'data_log'
