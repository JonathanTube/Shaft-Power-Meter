from peewee import CharField, TextField, Check, ForeignKeyField, DateTimeField
from src.db.base import BaseModel
from src.db.models.breach_reason import BreachReason


class BreachLog(BaseModel):
    breach_reason = ForeignKeyField(
        BreachReason, index=True, backref="BreachLog", verbose_name="功率突破原因")

    started_at = DateTimeField(null=False, constraints=[
                               Check("started_at IS NOT NULL")], verbose_name="功率突破发生时间")

    ship_position_when_started = CharField(
        max_length=100, verbose_name="发生功率突破时的船舶位置")

    ended_at = DateTimeField(null=True, verbose_name="功率突破结束时间")

    ship_position_when_ended = CharField(null=True,
                                         max_length=100, verbose_name="功率恢复到正常时的船舶位置")

    note = TextField(null=True, verbose_name="备注说明")

    class Meta:
        table_name = 'breach_log'
