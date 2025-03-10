from peewee import CharField
from src.database.base import BaseModel, db


class Preference(BaseModel):
    system_unit = CharField(verbose_name="系统单位: SI-0, Metric-1")

    language = CharField(verbose_name="语言 English-0, ")

    data_refresh_interval = CharField(verbose_name="页面数据刷新间隔, 默认5s")

    class Meta:
        table_name = 'preference'


with db:
    db.create_tables([Preference], safe=True)
