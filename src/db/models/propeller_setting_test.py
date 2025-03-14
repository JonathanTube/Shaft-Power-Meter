import pytest
from peewee import SqliteDatabase
from src.db.models.propeller_setting import PropellerSetting


@pytest.fixture(scope="module", autouse=True)
def setUp():
    db = SqliteDatabase(':memory:')
    PropellerSetting._meta.database = db
    db.connect()
    db.create_tables([PropellerSetting])
    yield  # 在此处暂停，等待测试执行
    # 清理数据库
    db.drop_tables([PropellerSetting])
    db.close()


@pytest.fixture(autouse=True)
def clear_data():
    """每个测试后清空数据，防止状态泄漏"""
    yield
    PropellerSetting.delete().execute()


# 通用有效测试数据模板
@pytest.fixture
def valid_data():
    return {
        'rpm_of_mcr_operating_point': 105.1,
        'shaft_power_of_mcr_operating_point': 18400,


        'rpm_left_of_normal_propeller_curve': 79.5,
        'bhp_left_of_normal_propeller_curve': 50.0,
        'rpm_right_of_normal_propeller_curve': 100.0,
        'bhp_right_of_normal_propeller_curve': 1000.0,
        'line_color_of_normal_propeller_curve': '#FFFFFF',


        'value_of_light_propeller_curve': 5.0,
        'line_color_of_light_propeller_curve': '#FFFFFF',


        'value_of_speed_limit_curve': 105,
        'line_color_of_speed_limit_curve': '#FFFFFF',


        'rpm_left_of_torque_load_limit_curve': 70,
        'bhp_left_of_torque_load_limit_curve': 51.0,
        'rpm_right_of_torque_load_limit_curve': 97.0,
        'bhp_right_of_torque_load_limit_curve': 97.5,
        'line_color_of_torque_load_limit_curve': '#FFFFFF',


        'value_of_overload_curve': 5.0,
        'line_color_of_overload_curve': '#000000',
        'alarm_enabled_of_overload_curve': True
    }

# --------------------------
# 创建（Create）测试
# --------------------------


def test_create_valid_propeller_setting(valid_data):
    """应能成功创建有效记录"""
    setting = PropellerSetting.create(**valid_data)
    assert setting.id != None
    assert setting.alarm_enabled_of_overload_curve == True

# --------------------------
# 读取（Read）测试
# --------------------------


def test_retrieve_propeller_setting(valid_data):
    """应正确查询已保存的记录"""
    created_setting = PropellerSetting.create(**valid_data)
    fetched_setting = PropellerSetting.get_by_id(created_setting.id)

    assert created_setting.id == fetched_setting.id
    assert fetched_setting.rpm_of_mcr_operating_point == 105.1

# --------------------------
# 更新（Update）测试
# --------------------------


def test_update_rpm_left_percent(valid_data):
    """应能安全更新允许范围内的百分比值"""
    # 初始创建
    setting = PropellerSetting.create(**valid_data)

    # 执行更新
    query = (
        PropellerSetting
        .update(rpm_left_of_normal_propeller_curve=85.0)
        .where(PropellerSetting.id == setting.id)
    )
    updated_count = query.execute()
    assert updated_count == 1

    # 验证更新结果
    updated_setting = PropellerSetting.get_by_id(setting.id)
    assert updated_setting.rpm_left_of_normal_propeller_curve == 85.0

# --------------------------
# 删除（Delete）测试
# --------------------------


def test_delete_propeller_setting(valid_data):
    """应能正确删除记录"""
    setting = PropellerSetting.create(**valid_data)
    setting_id = setting.id

    setting.delete_instance()

    with pytest.raises(PropellerSetting.DoesNotExist):
        PropellerSetting.get_by_id(setting_id)
