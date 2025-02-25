from .base import db
from .models.ship_info import ShipInfo
from .models.propeller_setting import PropellerSetting
from .models.breach_reason import BreachReason
from .models.breach_log import BreachLog


def initialize_db():
    db.connect()
    # 注意顺序：先创建无外键约束的表
    tables = [ShipInfo]
    # Peewee 默认使用 safe=True 模式创建表，若表已存在，不会覆盖或修改旧表结构
    db.create_tables(tables, safe=True)
    db.close()


__all__ = ['db', 'initialize_db', 'ShipInfo',
           'PropellerSetting', 'BreachReason', 'BreachLog']
