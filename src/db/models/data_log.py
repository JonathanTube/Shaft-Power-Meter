from peewee import BigIntegerField, IntegerField, FloatField, DateTimeField, CharField, BooleanField
from ..base import BaseModel


class DataLog(BaseModel):
    utc_date_time = DateTimeField(verbose_name="UTC日期时间")

    name = CharField(verbose_name="名称:sps or sps2")

    ad_0_torque = IntegerField(verbose_name="扭矩(Nm)")

    ad_1_thrust = IntegerField(verbose_name="推力(N)")

    speed = FloatField(verbose_name="转速(RPM)")

    power = IntegerField(verbose_name="功率(W)")

    energy = BigIntegerField(verbose_name="总能量:power * 采样时长")

    is_overload = BooleanField(verbose_name="是否过载", default=False)

    class Meta:
        table_name = 'data_log'
