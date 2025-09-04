from peewee import CharField, ForeignKeyField, DateTimeField
from db.models.event_log import EventLog
from ..base import BaseModel


class ReportInfo(BaseModel):
    event_log = ForeignKeyField(
        EventLog, index=True, backref="ReportInfo", verbose_name="事件日志"
    )

    utc_date_time = DateTimeField()

    report_name = CharField()

    class Meta:
        table_name = 'report_info'
