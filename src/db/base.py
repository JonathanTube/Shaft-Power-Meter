import os
from peewee import SqliteDatabase, DateTimeField, Model, IntegerField
from datetime import datetime

# Get the absolute path to the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, 'main.db')

db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    """ 所有模型的基类 """
    class Meta:
        database = db  # 统一继承数据库连接

    id = IntegerField(primary_key=True)

    created_at = DateTimeField(default=datetime.now)

    update_at = DateTimeField(default=datetime.now)
