from peewee import BigIntegerField, CharField
from ..base import BaseModel


class CounterLog(BaseModel):
    sps_name = CharField(verbose_name="sps name: sps or sps2")

    sum_speed = BigIntegerField(verbose_name="累积转速(RPM)", default=0)

    sum_power = BigIntegerField(verbose_name="累积功率(W)", default=0)

    times = BigIntegerField(verbose_name="累积次数", default=0)

    seconds = BigIntegerField(verbose_name="累计运行秒", default=0)

    class Meta:
        table_name = 'counter_log'
