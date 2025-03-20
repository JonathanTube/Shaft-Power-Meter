from peewee import CharField
from ..base import BaseModel, db


class ReportInfo(BaseModel):
    report_name = CharField()

    class Meta:
        table_name = 'report_info'
