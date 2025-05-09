from peewee import IntegerField
from ..base import BaseModel


class TestModeConf(BaseModel):
    min_torque = IntegerField(verbose_name="最小扭矩", default=0)

    max_torque = IntegerField(verbose_name="最大扭矩", default=0)

    min_speed = IntegerField(verbose_name="最小转速", default=0)

    max_speed = IntegerField(verbose_name="最大转速", default=0)
    
    min_thrust = IntegerField(verbose_name="最小推力", default=0)

    max_thrust = IntegerField(verbose_name="最大推力", default=0)

    class Meta:
        table_name = 'test_mode_conf'
