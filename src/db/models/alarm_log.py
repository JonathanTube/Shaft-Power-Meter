from peewee import IntegerField, DateTimeField, BooleanField
from ..base import BaseModel


class AlarmLog(BaseModel):
    utc_date_time = DateTimeField(verbose_name="UTC日期时间")

    alarm_type = IntegerField(verbose_name="告警类型")

    acknowledge_time = DateTimeField(verbose_name="确认时间", null=True)

    is_recovery = BooleanField(verbose_name="是否恢复", default=False)

    is_sync = BooleanField(verbose_name="是否同步", default=False)

    is_from_master = BooleanField(verbose_name="是否来自于master", default=False)

    master_alarm_id = IntegerField(verbose_name='主机的alarm_id', null=True)

    slave_alarm_id = IntegerField(verbose_name='从机的alarm_id', null=True)

    class Meta:
        table_name = 'alarm_log'
