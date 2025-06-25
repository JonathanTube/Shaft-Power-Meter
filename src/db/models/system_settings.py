from peewee import IntegerField, BooleanField, FloatField
from ..base import BaseModel


class SystemSettings(BaseModel):
    is_master = BooleanField(verbose_name="是否主机", default=True)

    is_individual = BooleanField(verbose_name="是否单机", default=True)

    enable_gps = BooleanField(verbose_name="启用GPS", default=False)

    display_thrust = BooleanField(verbose_name="是否显示推力", default=False)

    amount_of_propeller = IntegerField(verbose_name="螺旋桨数量 1-单桨 2-双桨", default=1)

    sha_po_li = BooleanField(verbose_name="是否开启ShaPoLi功能", default=False)

    eexi_limited_power = FloatField(null=True, verbose_name="EEXI 限制最大功率")

    eexi_breach_checking_duration = IntegerField(null=True, verbose_name="EEXI 超限检查时长")

    display_propeller_curve = BooleanField(verbose_name="是否显示螺旋桨曲线", default=True)

    hide_admin_account = BooleanField(verbose_name="是否隐藏admin账号", default=False)

    class Meta:
        table_name = 'system_settings'
