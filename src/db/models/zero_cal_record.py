from peewee import FloatField, ForeignKeyField

from src.db.base import BaseModel
from src.db.models.zero_cal_info import ZeroCalInfo


class ZeroCalRecord(BaseModel):
    zero_cal_info = ForeignKeyField(
        ZeroCalInfo,
        backref='records',
        on_delete='CASCADE',
        verbose_name="关联的调零信息")

    torque = FloatField(verbose_name="扭矩相关数值")

    thrust = FloatField(verbose_name="推力相关数值")

    class Meta:
        table_name = 'zero_cal_record'
