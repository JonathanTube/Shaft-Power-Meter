from peewee import FloatField, DateField, TimeField
from ..base import BaseModel, db


class DataLog(BaseModel):
    utc_date = DateField(verbose_name="UTC日期")

    utc_time = TimeField(verbose_name="UTC时间")

    revolution = FloatField(verbose_name="转速(Rev/Min)")

    power = FloatField(verbose_name="功率(kW)")

    thrust = FloatField(verbose_name="推力(kN)")

    torque = FloatField(verbose_name="扭矩(kNm)")

    class Meta:
        table_name = 'data_log'


with db:
    db.create_tables([DataLog], safe=True)
