from peewee import DateField, TimeField, BooleanField, CharField, DateTimeField

from ..base import BaseModel


class DateTimeConf(BaseModel):
    utc_date = DateField(verbose_name="utc-日期", null=True)

    utc_time = TimeField(verbose_name="utc-时间", null=True)

    system_date = DateField(verbose_name="操作系统-日期", null=True)

    system_time = TimeField(verbose_name="操作系统-时间", null=True)

    sync_with_gps = BooleanField(verbose_name="同步GPS日期时间", default=False)

    date_time_format = CharField(
        verbose_name="日期时间格式", default="YYYY-MM-dd HH:mm:ss")

    class Meta:
        table_name = 'date_time_conf'
