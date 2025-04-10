import os
import sys
from peewee import SqliteDatabase, DateTimeField, Model, IntegerField
from datetime import datetime

# Get the absolute path to the project root directory
# PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 # 如果是打包环境（PyInstaller临时目录）
if getattr(sys, 'frozen', False):
    PROJECT_ROOT = sys._MEIPASS  # PyInstaller解压目录
else:
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))  # 本地开发目录
    
DB_PATH = os.path.join(PROJECT_ROOT, 'main.db')

# 配置日志
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)  # ▶ 关键设置

db = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    """ 所有模型的基类 """
    class Meta:
        database = db  # 统一继承数据库连接

    id = IntegerField(primary_key=True)

    created_at = DateTimeField(default=datetime.now)

    update_at = DateTimeField(default=datetime.now)
