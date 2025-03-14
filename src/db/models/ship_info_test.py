import pytest
from peewee import SqliteDatabase, IntegrityError
from src.db.models.ship_info import ShipInfo, BaseModel


@pytest.fixture(scope="module", autouse=True)
def setup():
    """测试前：初始化内存数据库和表"""
    db = SqliteDatabase(':memory:')  # 使用内存数据库保证测试隔离
    BaseModel._meta.database = db
    db.connect()
    db.create_tables([ShipInfo])
    yield  # 在此处暂停，等待测试执行
    # 清理数据库
    db.drop_tables([ShipInfo])
    db.close()


@pytest.fixture(autouse=True)
def clear_data():
    """每个测试后清空数据，防止状态泄漏"""
    yield
    ShipInfo.delete().execute()


def test_create_ship_success():
    """测试正常创建船舶成功"""
    ship = ShipInfo.create(
        ship_type="散货船",
        ship_name="海洋之星",
        imo_number=1234567,
        dwt=80000.0,
        gt=40000.0,
        max_unlimited_power=5000.0,
        limited_power=3000.0
    )
    assert ship.ship_name == "海洋之星"
    assert ship.id > 0


def test_create_ship_invalid_imo():
    """测试IMO编号超出范围"""
    with pytest.raises(IntegrityError):
        ShipInfo.create(
            ship_name="测试船",
            imo_number=99999,  # 无效的6位数
            ship_type="测试类型",
            dwt=1, gt=1, max_unlimited_power=1, limited_power=1
        )


def test_create_ship_duplicate_imo():
    """测试IMO编号唯一性约束"""
    imo = 7654321
    ShipInfo.create(ship_name="船A", imo_number=imo, ship_type="类型A",
                    dwt=1, gt=1, max_unlimited_power=1, limited_power=1)
    with pytest.raises(IntegrityError):
        ShipInfo.create(ship_name="船B", imo_number=imo, ship_type="类型B",
                        dwt=2, gt=2, max_unlimited_power=2, limited_power=2)

# ---------- 更新测试 -----------


def test_update_ship_power():
    """测试更新功率字段"""
    ship = ShipInfo.create(
        ship_name="测试更新",
        imo_number=1111111,
        ship_type="油轮",
        dwt=50000,
        gt=30000,
        max_unlimited_power=6000,
        limited_power=4000
    )

    # 修改无限功率字段
    updated = (ShipInfo
               .update(max_unlimited_power=6500)
               .where(ShipInfo.id == ship.id)
               .execute())
    updated_ship = ShipInfo.get_by_id(ship.id)

    assert updated_ship.max_unlimited_power == 6500


def test_update_ship_invalid_dwt():
    """测试修改DWT为非法值"""
    ship = ShipInfo.create(ship_name="非法值测试船", imo_number=2222222,
                           ship_type="测试", dwt=100, gt=100,
                           max_unlimited_power=1, limited_power=1)
    with pytest.raises(IntegrityError):  # Peewee会触发DataError异常
        ship.dwt = -500.0
        ship.save()

# ---------- 删除测试 -----------


def test_delete_ship():
    """测试删除船舶"""
    ship = ShipInfo.create(ship_name="待删除", imo_number=3333333,
                           ship_type="类型", dwt=200, gt=200,
                           max_unlimited_power=2, limited_power=2)
    ship_id = ship.id
    ship.delete_instance()

    with pytest.raises(ShipInfo.DoesNotExist):
        ShipInfo.get_by_id(ship_id)

# ---------- 查询测试 -----------


def test_query_by_ship_name():
    """测试通过船名查询"""
    ShipInfo.create(ship_name="查询测试船", imo_number=4444444,
                    ship_type="测试", dwt=300, gt=300,
                    max_unlimited_power=3, limited_power=3)
    result = ShipInfo.get(ShipInfo.ship_name == "查询测试船")
    assert result.imo_number == 4444444
