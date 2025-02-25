import unittest
from peewee import SqliteDatabase, IntegrityError
from src.database.models.breach_reason import BreachReason, BaseModel


class TestBreachReasonCRUD(unittest.TestCase):
    def setUp(self):
        self.db = SqliteDatabase(':memory:')
        BaseModel._meta.database = self.db
        self.db.connect()
        self.db.create_tables([BreachReason])

    def tearDown(self):
        """测试后：清理资源"""
        self.db.drop_tables([BreachReason])
        self.db.close()

    # ---------- 创建测试 -----------
    def test_create_reason_success(self):
        reason = 'test reason'
        breachReason = BreachReason.create(
            reason=reason
        )
        self.assertEqual(breachReason.reason, reason)
        self.assertTrue(breachReason.id > 0)

    def test_create_breach_reason_invalid_imo(self):
        with self.assertRaises(IntegrityError):
            BreachReason.create(reason="")

    # ---------- 更新测试 -----------
    def test_update_breach_reason(self):
        breachReason = BreachReason.create(reason="测试更新")

        updated = (BreachReason
                   .update(reason='updated')
                   .where(BreachReason.id == breachReason.id)
                   .execute())

        updated_breach_reason = BreachReason.get_by_id(breachReason.id)

        self.assertEqual(updated_breach_reason.reason, 'updated')

    # ---------- 删除测试 -----------
    def test_delete_breach_reason(self):
        breach_reason = BreachReason.create(reason="待删除")
        breach_reason_id = breach_reason.id
        breach_reason.delete_instance()

        with self.assertRaises(BreachReason.DoesNotExist):
            BreachReason.get_by_id(breach_reason_id)


if __name__ == '__main__':
    unittest.main()
