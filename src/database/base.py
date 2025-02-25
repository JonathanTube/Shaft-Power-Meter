from peewee import SqliteDatabase, DateTimeField, Model
from datetime import datetime
db = SqliteDatabase('main.db')


class BaseModel(Model):
    """ 所有模型的基类 """
    class Meta:
        database = db  # 统一继承数据库连接

    created_at = DateTimeField(default=datetime.now)

    update_at = DateTimeField(default=datetime.now)
