import pytest
from peewee import SqliteDatabase, IntegrityError
from src.database.models.breach_reason import BreachReason, BaseModel


@pytest.fixture(scope="module", autouse=True)
def setup():
    db = SqliteDatabase(':memory:')
    BaseModel._meta.database = db
    db.connect()
    db.create_tables([BreachReason])
    yield  # 在此处暂停，等待测试执行
    # 清理数据库
    db.drop_tables([BreachReason])
    db.close()


@pytest.fixture(autouse=True)
def clear_data():
    """每个测试后清空数据，防止状态泄漏"""
    yield
    BreachReason.delete().execute()
# ---------- 创建测试 -----------


def test_create_reason_success():
    reason = 'test reason'
    breachReason = BreachReason.create(
        reason=reason
    )
    assert breachReason.reason == reason
    assert breachReason.id > 0


def test_create_breach_reason_invalid_imo():
    with pytest.raises(IntegrityError):
        BreachReason.create(reason="")

# ---------- 更新测试 -----------


def test_update_breach_reason():
    breachReason = BreachReason.create(reason="测试更新")

    updated = (BreachReason
               .update(reason='updated')
               .where(BreachReason.id == breachReason.id)
               .execute())

    updated_breach_reason = BreachReason.get_by_id(breachReason.id)

    assert updated_breach_reason.reason == 'updated'

# ---------- 删除测试 -----------


def test_delete_breach_reason():
    breach_reason = BreachReason.create(reason="待删除")
    breach_reason_id = breach_reason.id
    breach_reason.delete_instance()

    with pytest.raises(BreachReason.DoesNotExist):
        BreachReason.get_by_id(breach_reason_id)
