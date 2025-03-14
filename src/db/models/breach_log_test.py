import pytest
from peewee import SqliteDatabase
from src.db.models.breach_log import BreachLog, BaseModel
from src.db.models.breach_reason import BreachReason
from datetime import datetime


@pytest.fixture(scope="module", autouse=True)
def setup():
    db = SqliteDatabase(':memory:')
    BaseModel._meta.database = db
    db.connect()
    db.create_tables([BreachLog, BreachReason])
    yield  # 在此处暂停，等待测试执行
    # 清理数据库
    db.drop_tables([BreachLog, BreachReason])
    db.close()


@pytest.fixture(autouse=True)
def clear_data():
    """每个测试后清空数据，防止状态泄漏"""
    yield
    BreachLog.delete().execute()
    BreachReason.delete().execute()


# ---------- 创建测试 -----------


@pytest.fixture
def valid_data():
    breachReason = BreachReason.create(reason="operating in adverse weather")
    return {
        'breach_reason': breachReason,
        'started_at': datetime.now(),
        'ship_position_when_started': '-35°1′7.4599″S 138°33′44.1263″E',
        'note': 'long text long text long text long text long text long text long text long text long text long text'
    }


def test_create_breach_log_success(valid_data):
    breachLog = BreachLog.create(**valid_data)
    assert breachLog.id > 0


# ---------- 更新测试 -----------


def test_update_breach_reason(valid_data):
    reason2 = 'opearting in ice-infested waters'

    breachReason2 = BreachReason.create(reason=reason2)

    breachLog = BreachLog.create(**valid_data)

    BreachLog.update(
        ended_at=datetime.now(),
        ship_position_when_ended='-35°1′7.4599″S 138°33′44.1263″E',
        breach_reason=breachReason2
    ).where(BreachLog.id == breachLog.id).execute()

    updated_breach_reason = BreachLog.get_by_id(BreachLog.id)

    assert updated_breach_reason.breach_reason.reason == reason2

# ---------- 删除测试 -----------


def test_delete_breach_reason(valid_data):
    breach_reason = BreachLog.create(**valid_data)
    breach_reason_id = breach_reason.id
    breach_reason.delete_instance()

    with pytest.raises(BreachLog.DoesNotExist):
        BreachLog.get_by_id(breach_reason_id)
