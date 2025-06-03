from peewee import FloatField, ForeignKeyField,CharField

from ..base import BaseModel
from .zero_cal_info import ZeroCalInfo


class ZeroCalRecord(BaseModel):
    zero_cal_info = ForeignKeyField(
        ZeroCalInfo,
        backref='records',
        on_delete='CASCADE',
        verbose_name="关联的调零信息")

    name = CharField(verbose_name="用户名")

    mv_per_v_for_torque = FloatField(verbose_name="扭矩 - mv/v")

    mv_per_v_for_thrust = FloatField(verbose_name="推力 - mv/v")

    class Meta:
        table_name = 'zero_cal_record'
