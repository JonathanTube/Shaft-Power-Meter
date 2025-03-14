from peewee import DateField, TimeField, BooleanField, CharField

from src.db.base import BaseModel, db


class DateTimeConf(BaseModel):
    utc_date = DateField(verbose_name="utc-日期")

    utc_time = TimeField(verbose_name="utc-时间")

    system_date = DateField(verbose_name="操作系统-日期")

    system_time = TimeField(verbose_name="操作系统-时间")

    sync_with_gps = BooleanField(verbose_name="同步GPS日期时间")

    date_time_format = CharField(verbose_name="日期时间格式")

    class Meta:
        table_name = 'date_time_conf'


with db:
    db.create_tables([DateTimeConf], safe=True)
