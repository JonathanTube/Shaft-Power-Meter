import hashlib
from peewee import CharField, IntegerField
from ..base import BaseModel


class User(BaseModel):
    user_name = CharField(verbose_name="用户名")

    user_pwd = CharField(verbose_name="密码", max_length=255)

    user_role = IntegerField(verbose_name="角色")

    def set_password(self, password):
        """设置密码（自动加密）"""
        # 使用更安全的SHA256替代MD5
        self.user_pwd = hashlib.sha256(password.encode()).hexdigest()
        
    def check_password(self, password):
        """验证密码"""
        return self.user_pwd == hashlib.sha256(password.encode()).hexdigest()


    class Meta:
        table_name = 'user'