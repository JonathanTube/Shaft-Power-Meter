from peewee import FloatField, CharField
from ..base import BaseModel


class CounterLog(BaseModel):
    category = CharField(
        max_length=20, verbose_name="类型:Interval、Manually、Total")
    sum_power = FloatField(verbose_name="总计能耗(kWh)")
    average_power = FloatField(verbose_name="平均功率(kW)")
    revolution = FloatField(verbose_name="旋转圈数")
    average_revolution = FloatField(verbose_name="平均转速(rpm)")

    class Meta:
        table_name = 'breach_reason'
