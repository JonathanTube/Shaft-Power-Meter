from peewee import FloatField
from src.db.base import BaseModel


class DataLog(BaseModel):
    revolution = FloatField(verbose_name="转速(Rev/Min)")

    power = FloatField(verbose_name="功率(kW)")

    thrust = FloatField(verbose_name="推力(kN)")

    torque = FloatField(verbose_name="扭矩(kNm)")

    class Meta:
        table_name = 'data_log'
