from peewee import IntegerField,BooleanField
from ..base import BaseModel


class Preference(BaseModel):
    theme = IntegerField(verbose_name="主题: Light-0, Dark-1", default=0)

    fullscreen = BooleanField(verbose_name="是否全屏", default=False)

    system_unit = IntegerField(verbose_name="系统单位: SI-0, Metric-1", default=0)

    language = IntegerField(verbose_name="语言 English-0, Chinese-1", default=0)

    data_refresh_interval = IntegerField(verbose_name="页面数据刷新间隔, 默认5s", default=5)

    class Meta:
        table_name = 'preference'
