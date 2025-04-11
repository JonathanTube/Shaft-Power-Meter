from peewee import FloatField, ForeignKeyField, DateTimeField

from db.models.report_info import ReportInfo
from ..base import BaseModel


class ReportDetail(BaseModel):
    report_info = ForeignKeyField(ReportInfo, index=True, backref="ReportInfo", verbose_name="报告")

    utc_date_time = DateTimeField()

    speed = FloatField()

    torque = FloatField()

    power = FloatField()

    total_power = FloatField()

    class Meta:
        table_name = 'report_detail'
