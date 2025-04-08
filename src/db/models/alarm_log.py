from peewee import CharField, DateTimeField
from ..base import BaseModel


class AlarmLog(BaseModel):
    utc_date_time = DateTimeField(verbose_name="UTC日期时间")

    event_name = CharField(verbose_name="事件名称")

    acknowledge_time = DateTimeField(verbose_name="确认时间")

    class Meta:
        table_name = 'alarm_log'
