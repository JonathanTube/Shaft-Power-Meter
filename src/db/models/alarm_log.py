from peewee import IntegerField, DateTimeField
from ..base import BaseModel


class AlarmLog(BaseModel):
    utc_date_time = DateTimeField(verbose_name="UTC日期时间")

    alarm_type = IntegerField(verbose_name="告警类型")

    acknowledge_time = DateTimeField(verbose_name="确认时间", null=True)

    class Meta:
        table_name = 'alarm_log'
