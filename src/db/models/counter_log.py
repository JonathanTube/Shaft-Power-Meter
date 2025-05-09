from peewee import IntegerField, BigIntegerField, CharField, DateTimeField
from ..base import BaseModel


class CounterLog(BaseModel):
    counter_type = IntegerField(verbose_name="类型: 1-manually 2-total")

    sps_name = CharField(verbose_name="sps name: sps1 or sps2")

    total_speed = BigIntegerField(verbose_name="累积转速(RPM)", default=0)

    total_power = BigIntegerField(verbose_name="累积功率(W)", default=0)

    times = BigIntegerField(verbose_name="累积次数", default=0)

    start_utc_date_time = DateTimeField(verbose_name="开始时间")

    stop_utc_date_time = DateTimeField(verbose_name="停止时间", null=True)

    counter_status = CharField(verbose_name="stopped, running, reset", default="stopped")

    class Meta:
        table_name = 'counter_log'
