import pytest
from peewee import SqliteDatabase
from src.database.models.report_info import ReportInfo, BaseModel


@pytest.fixture(scope="module", autouse=True)
def setUp():
    db = SqliteDatabase(':memory:')
    BaseModel._meta.database = db
    db.connect()
    db.create_tables([ReportInfo])
    yield  # 在此处暂停，等待测试执行
    # 清理数据库
    db.drop_tables([ReportInfo])
    db.close()


@pytest.fixture(autouse=True)
def clear_data():
    """每个测试后清空数据，防止状态泄漏"""
    yield
    ReportInfo.delete().execute()


def test_create_report_info():
    # Create a new ReportInfo instance
    report = ReportInfo.create(
        report_name='Test Report',
        start_at='2023-01-01 00:00:00',
        end_at='2023-01-02 00:00:00'
    )
    # Verify the report was created
    assert ReportInfo.select().count() == 1
    assert report.report_name == 'Test Report'


def test_delete_report_info():
    # Create a new ReportInfo instance
    report = ReportInfo.create(
        report_name='Test Report',
        start_at='2023-01-01 00:00:00',
        end_at='2023-01-02 00:00:00'
    )
    # Delete the report
    report.delete_instance()
    # Verify the report was deleted
    assert ReportInfo.select().count() == 0
