from peewee import CharField, DateTimeField
from src.database.base import BaseModel


class ReportInfo(BaseModel):
    report_name = CharField(max_length=255)
    start_at = DateTimeField()
    end_at = DateTimeField()

    class Meta:
        table_name = 'report_info'
