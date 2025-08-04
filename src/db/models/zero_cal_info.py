from peewee import DateTimeField, FloatField, IntegerField, CharField

from ..base import BaseModel


class ZeroCalInfo(BaseModel):
    utc_date_time = DateTimeField(verbose_name="utc日期时间")

    name = CharField(verbose_name="浆名称")

    torque_offset = FloatField(verbose_name="扭矩-偏移量", null=True)

    thrust_offset = FloatField(verbose_name="推力-偏移量", null=True)

    class Meta:
        table_name = 'zero_cal_info'
