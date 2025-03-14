import pytest
from peewee import SqliteDatabase
from src.db.models.counter_log import CounterLog, BaseModel


@pytest.fixture(scope="module", autouse=True)
def setUp():
    db = SqliteDatabase(':memory:')
    BaseModel._meta.database = db
    db.connect()
    db.create_tables([CounterLog])
    yield  # 在此处暂停，等待测试执行
    # 清理数据库
    db.drop_tables([CounterLog])
    db.close()


@pytest.fixture(autouse=True)
def clear_data():
    """每个测试后清空数据，防止状态泄漏"""
    yield
    CounterLog.delete().execute()


# ---------- 创建测试 -----------


@pytest.fixture
def valid_data():
    return {
        'category': 'interval',
        'sum_power': 100,
        'average_power': 20,
        'revolution': 100,
        'average_revolution': 30
    }


def test_create_counter_log_success(valid_data):
    counterLog = CounterLog.create(**valid_data)
    assert counterLog.id > 0
