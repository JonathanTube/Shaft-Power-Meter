from peewee import FloatField, ForeignKeyField, DateTimeField, CharField

from db.models.report_info import ReportInfo
from ..base import BaseModel


class ReportDetail(BaseModel):

    report_info = ForeignKeyField(ReportInfo, index=True, backref="ReportInfo", verbose_name="报告")

    name = CharField(verbose_name="名称:sps1/sps2")

    utc_date_time = DateTimeField()

    speed = FloatField()

    torque = FloatField()

    power = FloatField()

    total_power = FloatField()

    class Meta:
        table_name = 'report_detail'
