from peewee import CharField, TextField, ForeignKeyField, DateTimeField, IntegerField, FloatField
from ..base import BaseModel
from .breach_reason import BreachReason


class EventLog(BaseModel):
    breach_reason = ForeignKeyField(
        BreachReason, null=True, index=True, backref="EventLog", verbose_name="功率突破原因"
    )

    started_at = DateTimeField(null=True, verbose_name="功率突破发生时间")

    started_position = CharField(null=True, verbose_name="发生功率突破时的船舶位置")

    ended_at = DateTimeField(null=True, verbose_name="功率突破结束时间")

    ended_position = CharField(null=True, verbose_name="功率恢复到正常时的船舶位置")

    acknowledged_at = DateTimeField(null=True, verbose_name="功率突破确认时间(mute)")

    note = TextField(null=True, verbose_name="备注说明")

    beaufort_number = TextField(null=True, verbose_name="风力等级")

    wave_height = TextField(null=True, verbose_name="浪高")

    ice_condition = TextField(null=True, verbose_name="冰况")

    class Meta:
        table_name = 'event_log'
