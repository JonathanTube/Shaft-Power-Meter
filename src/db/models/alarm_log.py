from peewee import CharField, DateTimeField, BooleanField, IntegerField
from ..base import BaseModel


class AlarmLog(BaseModel):
    utc_date_time = DateTimeField(verbose_name="UTC日期时间")

    alarm_type = CharField(verbose_name="告警类型")

    acknowledge_time = DateTimeField(verbose_name="确认时间", null=True)

    is_recovery = BooleanField(verbose_name="是否恢复记录", default=False)

    is_sync = BooleanField(verbose_name="是否同步", default=False)

    is_from_master = BooleanField(verbose_name="是否来自于master", default=False)

    outer_id = IntegerField(verbose_name="外部id, 如果是slave同步的master数据, 就是master中alarmLog.id，否则相反。", null=True)

    class Meta:
        table_name = 'alarm_log'
