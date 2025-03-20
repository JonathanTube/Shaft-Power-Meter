from peewee import CharField, TimeField, DateField
from ..base import BaseModel, db


class GpsLog(BaseModel):
    utc_date = DateField(verbose_name="UTC日期")

    utc_time = TimeField(verbose_name="UTC时间")

    longitude = CharField(verbose_name="经度")

    latitude = CharField(verbose_name="纬度")

    class Meta:
        table_name = 'gps_log'
