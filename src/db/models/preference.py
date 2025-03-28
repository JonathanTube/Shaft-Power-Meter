from peewee import IntegerField
from ..base import BaseModel


class Preference(BaseModel):
    theme = IntegerField(verbose_name="主题: Auto-0, Light-1, Dark-2")

    system_unit = IntegerField(verbose_name="系统单位: SI-0, Metric-1")

    language = IntegerField(verbose_name="语言 English-0, Chinese-1")

    data_refresh_interval = IntegerField(verbose_name="页面数据刷新间隔, 默认5s")

    class Meta:
        table_name = 'preference'
