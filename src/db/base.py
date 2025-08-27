import os
import sys
from peewee import SqliteDatabase, DateTimeField, Model, IntegerField
from datetime import datetime

# 选择可写的数据库目录
if getattr(sys, 'frozen', False):
    # 打包环境：使用可写的可执行文件所在目录下的 data 子目录
    exe_dir = os.path.dirname(sys.executable)
    data_dir = os.path.join(exe_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    DB_PATH = os.path.join(data_dir, '988bbc4fc383')
else:
    # 本地开发：使用当前文件所在目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(project_root, '988bbc4fc383')

db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    """ 所有模型的基类 """
    class Meta:
        database = db  # 统一继承数据库连接

    id = IntegerField(primary_key=True)

    created_at = DateTimeField(default=datetime.now)

    update_at = DateTimeField(default=datetime.now)
