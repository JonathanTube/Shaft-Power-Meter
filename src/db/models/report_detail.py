from peewee import CharField, FloatField, ForeignKeyField, DateTimeField

from db.models.breach_reason import BreachReason
from db.models.report_info import ReportInfo
from ..base import BaseModel


class ReportDetail(BaseModel):
    report_info = ForeignKeyField(
        ReportInfo, index=True, backref="ReportInfo", verbose_name="报告")

    ship_type = CharField()

    ship_size = CharField()

    imo_number = CharField()

    ship_name = CharField()

    un_limited_power = FloatField()

    limited_power = FloatField()

    # start
    date_time_of_power_reserve_breach = DateTimeField()

    ship_position_of_power_reserve_breach = CharField()

    beaufort_number_of_power_reserve_breach = CharField()

    wave_height_of_power_reserve_breach = CharField()

    ice_condition_of_power_reserve_breach = CharField()

    # end
    date_time_when_returning_to_limited_power = DateTimeField()

    ship_position_when_returning_to_limited_power = CharField()

    beaufort_number_when_returning_to_limited_power = CharField()

    wave_height_when_returning_to_limited_power = CharField()

    ice_condition_when_returning_to_limited_power = CharField()

    # reason for common using.
    reason_for_using_the_power_reserve = ForeignKeyField(
        BreachReason, index=True, backref="BreachReason", verbose_name="使用备用功率原因")

    class Meta:
        table_name = 'report_detail'
