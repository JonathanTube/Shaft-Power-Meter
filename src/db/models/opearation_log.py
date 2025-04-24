from peewee import IntegerField, DateField, TextField
from ..base import BaseModel


class OperationLog(BaseModel):
    user_id = IntegerField(verbose_name="用户ID")

    utc_date_time = DateField(verbose_name="UTC时间")

    operation_type = IntegerField(verbose_name="操作类型")

    operation_content = TextField(verbose_name="操作内容")

    class Meta:
        table_name = 'operation_log'