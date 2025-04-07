from peewee import CharField, DateTimeField
from ..base import BaseModel


class GpsLog(BaseModel):
    utc_date_time = DateTimeField(verbose_name="UTC日期时间")

    location = CharField(verbose_name="坐标")

    class Meta:
        table_name = 'gps_log'
