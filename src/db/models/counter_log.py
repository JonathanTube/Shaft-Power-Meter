from peewee import BigIntegerField, CharField, DateTimeField
from ..base import BaseModel


class CounterLog(BaseModel):
    sps_name = CharField(verbose_name="sps name: sps or sps2")

    sum_speed = BigIntegerField(verbose_name="累积转速(RPM)", default=0)

    sum_power = BigIntegerField(verbose_name="累积功率(W)", default=0)

    times = BigIntegerField(verbose_name="累积次数", default=0)

    start_utc_date_time = DateTimeField(verbose_name="开始时间")

    class Meta:
        table_name = 'counter_log'
