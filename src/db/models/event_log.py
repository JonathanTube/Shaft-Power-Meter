from peewee import CharField, TextField, ForeignKeyField, DateTimeField
from ..base import BaseModel
from .breach_reason import BreachReason


class EventLog(BaseModel):
    breach_reason = ForeignKeyField(
        BreachReason, index=True, backref="BreachLog", verbose_name="功率突破原因"
    )

    started_at = DateTimeField(null=False, verbose_name="功率突破发生时间")

    started_position = CharField(verbose_name="发生功率突破时的船舶位置")

    ended_at = DateTimeField(null=True, verbose_name="功率突破结束时间")

    ended_position = CharField(null=True, verbose_name="功率恢复到正常时的船舶位置")

    note = TextField(null=True, verbose_name="备注说明")

    class Meta:
        table_name = 'breach_log'
