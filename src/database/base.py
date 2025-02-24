from peewee import SqliteDatabase, Model

db = SqliteDatabase('main.db')  

class BaseModel(Model):
    """ 所有模型的基类 """
    class Meta:
        database = db  # 统一继承数据库连接
