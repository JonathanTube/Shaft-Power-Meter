from peewee import IntegerField, DateTimeField, CharField, BooleanField
from ..base import BaseModel


class DataLog(BaseModel):
    utc_date_time = DateTimeField(verbose_name="UTC日期时间")

    name = CharField(verbose_name="名称:sps1 or sps2")

    speed = IntegerField(verbose_name="转速(RPM)")

    power = IntegerField(verbose_name="功率(W)")

    thrust = IntegerField(verbose_name="推力(N)")

    torque = IntegerField(verbose_name="扭矩(Nm)")

    is_overload = BooleanField(verbose_name="是否过载", default=False)

    class Meta:
        table_name = 'data_log'
