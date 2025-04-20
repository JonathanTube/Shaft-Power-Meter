from peewee import CharField, IntegerField
from ..base import BaseModel


class User(BaseModel):
    user_name = CharField(verbose_name="用户名")

    user_pwd = CharField(verbose_name="密码", default="123456")

    user_role = IntegerField(verbose_name="角色")

    class Meta:
        table_name = 'user'
