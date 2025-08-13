from peewee import CharField, DateTimeField, BooleanField
from ..base import BaseModel


class AlarmLog(BaseModel):
    alarm_uuid = CharField(verbose_name="告警类型")

    alarm_type = CharField(verbose_name="告警类型")

    occured_time = DateTimeField(verbose_name="发生时间")

    recovery_time = DateTimeField(verbose_name="恢复时间", null=True)

    acknowledge_time = DateTimeField(verbose_name="确认时间", null=True)

    out_of_sync = BooleanField(verbose_name="无需同步", default=False)

    is_synced = BooleanField(verbose_name="是否已同步", default=False)

    class Meta:
        table_name = 'alarm_log'
