import pytest
from peewee import SqliteDatabase
from src.db.models.gps_log import GpsLog, BaseModel
from datetime import datetime


@pytest.fixture(scope="module", autouse=True)
def setUp():
    db = SqliteDatabase(':memory:')
    BaseModel._meta.database = db
    db.connect()
    db.create_tables([GpsLog])
    yield  # 在此处暂停，等待测试执行
    # 清理数据库
    db.drop_tables([GpsLog])
    db.close()


@pytest.fixture(autouse=True)
def clear_data():
    """每个测试后清空数据，防止状态泄漏"""
    yield
    GpsLog.delete().execute()


# ---------- 创建测试 -----------


@pytest.fixture
def valid_data():
    utc_date = datetime.now().date()
    utc_time = datetime.now().time()
    return {
        'utc_date': utc_date,
        'utc_time': utc_time,
        'longitude': "5321.6802,N",
        'latitude': '00630.3372,W'
    }


def test_create_gps_log_success(valid_data):
    gpsLog = GpsLog.create(**valid_data)
    assert gpsLog.id > 0
