from peewee import CharField, Check
from ..base import BaseModel


class BreachReason(BaseModel):
    reason = CharField(
        max_length=500,
        null=False,              # 禁止数据库存储 NULL 值
        constraints=[
            Check("reason != ''")  # 确保字段值非空字符串
        ],
        help_text="原因必填，且不能为空",
        verbose_name="Reason Description for Power Reserve Breach"
    )

    class Meta:
        table_name = 'breach_reason'
