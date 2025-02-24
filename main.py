from src.database import ShipInfo, initialize_db, db

# db.drop_tables([ShipInfo], safe=True)

# 初始化数据库（应用启动时调用）
initialize_db()

# 查询所有散货船
bulk_carriers = ShipInfo.select()
