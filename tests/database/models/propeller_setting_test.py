import unittest
from datetime import datetime
from unittest import mock
from peewee import IntegrityError, SqliteDatabase
from src.database.models.propeller_setting import PropellerSetting


class TestPropellerSettingCRUD(unittest.TestCase):
    def setUp(self):
        self.db = SqliteDatabase(':memory:')  # 使用内存数据库保证测试隔离
        self.db.init(':memory:')
        self.db.connect()
        self.db.create_tables([PropellerSetting])

        # 通用有效测试数据模板
        self.valid_data = {
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

    def tearDown(self):
        self.db.drop_tables([PropellerSetting])
        self.db.close()

    # --------------------------
    # 创建（Create）测试
    # --------------------------
    def test_create_valid_propeller_setting(self):
        """应能成功创建有效记录"""
        setting = PropellerSetting.create(**self.valid_data)
        self.assertIsNotNone(setting.id)
        self.assertTrue(setting.alarm_enabled_of_overload_curve)

    # --------------------------
    # 读取（Read）测试
    # --------------------------
    def test_retrieve_propeller_setting(self):
        """应正确查询已保存的记录"""
        created_setting = PropellerSetting.create(**self.valid_data)
        fetched_setting = PropellerSetting.get_by_id(created_setting.id)

        self.assertEqual(created_setting.id, fetched_setting.id)
        self.assertEqual(fetched_setting.rpm_of_mcr_operating_point, 105.1)

    # --------------------------
    # 更新（Update）测试
    # --------------------------
    def test_update_rpm_left_percent(self):
        """应能安全更新允许范围内的百分比值"""
        # 初始创建
        setting = PropellerSetting.create(**self.valid_data)

        # 执行更新
        query = (
            PropellerSetting
            .update(rpm_left_of_normal_propeller_curve=85.0)
            .where(PropellerSetting.id == setting.id)
        )
        updated_count = query.execute()
        self.assertEqual(updated_count, 1)

        # 验证更新结果
        updated_setting = PropellerSetting.get_by_id(setting.id)
        self.assertEqual(
            updated_setting.rpm_left_of_normal_propeller_curve, 85.0)

    # --------------------------
    # 删除（Delete）测试
    # --------------------------
    def test_delete_propeller_setting(self):
        """应能正确删除记录"""
        setting = PropellerSetting.create(**self.valid_data)
        setting_id = setting.id

        setting.delete_instance()

        with self.assertRaises(PropellerSetting.DoesNotExist):
            PropellerSetting.get_by_id(setting_id)


if __name__ == '__main__':
    unittest.main(verbosity=2)
