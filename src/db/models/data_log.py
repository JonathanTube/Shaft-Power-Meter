from peewee import IntegerField, DateField, TimeField, CharField
from ..base import BaseModel


class DataLog(BaseModel):
    name = CharField(verbose_name="名称:SPS1 or SPS2")

    utc_date = DateField(verbose_name="UTC日期")

    utc_time = TimeField(verbose_name="UTC时间")

    speed = IntegerField(verbose_name="转速(RPM)")

    power = IntegerField(verbose_name="功率(W)")

    thrust = IntegerField(verbose_name="推力(N)")

    torque = IntegerField(verbose_name="扭矩(Nm)")

    rounds = IntegerField(verbose_name="圈数")

    class Meta:
        table_name = 'data_log'
