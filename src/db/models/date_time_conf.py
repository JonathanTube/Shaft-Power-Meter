from peewee import DateField, TimeField, BooleanField, CharField, DateTimeField

from ..base import BaseModel


class DateTimeConf(BaseModel):
    utc_date_time = DateTimeField(verbose_name="UTC-日期时间")

    system_date_time = DateTimeField(verbose_name="操作系统-日期时间")

    sync_with_gps = BooleanField(verbose_name="同步GPS日期时间", default=False)

    date_format = CharField(verbose_name="日期格式", default="YYYY-MM-dd")

    class Meta:
        table_name = 'date_time_conf'
