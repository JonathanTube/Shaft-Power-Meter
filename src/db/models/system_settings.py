from peewee import IntegerField, BooleanField, FloatField
from ..base import BaseModel


class SystemSettings(BaseModel):
    display_thrust = BooleanField(verbose_name="是否显示推力", default=False)

    amount_of_propeller = IntegerField(verbose_name="螺旋桨数量 1-单桨 2-双桨", default=1)

    sha_po_li = BooleanField(verbose_name="是否开启ShaPoLi功能", default=False)

    eexi_limited_power = IntegerField(null=True, verbose_name="EEXI 限制最大功率")

    eexi_breach_checking_duration = IntegerField(null=True, verbose_name="EEXI 超限检查时长")

    class Meta:
        table_name = 'system_settings'
