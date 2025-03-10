from peewee import IntegerField, BooleanField
from src.database.base import BaseModel,db


class SystemSettings(BaseModel):

    # running_mode = IntegerField(verbose_name="运行模式:0-Standalone 1-Master/Slave")

    # master_slave = IntegerField(verbose_name="主/从 0-Master 1-Slave")

    display_thrust = BooleanField(verbose_name="是否显示推力")

    amount_of_propeller = IntegerField(verbose_name="螺旋桨数量 1-单桨 2-双桨")

    sha_po_li = BooleanField(verbose_name="是否开启ShaPoLi功能")

    class Meta:
        table_name = 'system_settings'

with db:
    db.create_tables([SystemSettings], safe=True)