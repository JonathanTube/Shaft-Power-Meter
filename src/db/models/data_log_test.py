import pytest
from peewee import SqliteDatabase
from src.db.models.data_log import DataLog, BaseModel
import random


@pytest.fixture(scope="module", autouse=True)
def setUp():
    db = SqliteDatabase(':memory:')
    BaseModel._meta.database = db
    db.connect()
    db.create_tables([DataLog])
    yield
    db.drop_tables([DataLog])
    db.close()


@pytest.fixture(autouse=True)
def clear_data():
    """每个测试后清空数据，防止状态泄漏"""
    yield
    DataLog.delete().execute()


# ---------- 创建测试 -----------


@pytest.fixture
def valid_data():
    return {
        'revolution': round(random.uniform(100.0, 500.0), 2),
        'power': round(random.uniform(100.0, 500.0), 2),
        'thrust': round(random.uniform(100.0, 500.0), 2),
        'torque': round(random.uniform(100.0, 500.0), 2)
    }


def test_create_breach_log_success(valid_data):
    dataLog = DataLog.create(**valid_data)
    assert dataLog.id > 0


# ---------- 更新测试 -----------


def test_update_data_log(valid_data):
    dataLog = DataLog.create(**valid_data)

    DataLog.update(**valid_data).where(DataLog.id == dataLog.id).execute()

    updated_data_log = DataLog.get_by_id(dataLog.id)

    assert updated_data_log.id > 0

# # ---------- 删除测试 -----------


def test_delete_data_log(valid_data):
    data_log = DataLog.create(**valid_data)
    data_log_id = data_log.id
    data_log.delete_instance()

    with pytest.raises(DataLog.DoesNotExist):
        DataLog.get_by_id(data_log_id)
