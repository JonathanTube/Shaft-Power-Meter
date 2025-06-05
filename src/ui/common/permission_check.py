import flet as ft
from typing import Callable
from db.models.system_settings import SystemSettings
from db.models.user import User
from ui.common.toast import Toast


class PermissionCheck(ft.AlertDialog):
    def __init__(self, on_confirm: Callable, user_role: int = 0, on_cancel: Callable = None, closable: bool = True):
        super().__init__()
        self.modal = not closable
        self.user_role = user_role
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.closable = closable
        # self.barrier_color = ft.Colors.TRANSPARENT
        self.shadow_color = ft.Colors.PRIMARY
        self.elevation = 8

        self.system_settings:SystemSettings = SystemSettings.get()

    def get_role_name(self):
        if self.user_role == 0:
            return "Admin"
        elif self.user_role == 1:
            return "Master"
        elif self.user_role == 2:
            return "User"

    def build(self):
        s = self.page.session
        self.title = ft.Text(f"{self.get_role_name()}-{s.get('lang.permission.authentication')}")
        self.user_name = ft.Dropdown(
            width=300,
            label=self.page.session.get("lang.permission.user_name"),
            value=None,
            options=[]
        )
        self.user_pwd = ft.TextField(
            width=300,
            value="",
            label=s.get("lang.permission.user_pwd"),
            password=True,
            can_reveal_password=True
        )
        self.content = ft.Column(
            height=150,
            controls=[self.user_name, self.user_pwd]
        )
        self.actions = [
            ft.TextButton(s.get("lang.button.confirm"), on_click=self.__on_confirm),
            ft.TextButton(s.get("lang.button.cancel"), visible=self.closable, on_click=self.__on_cancel)
        ]

    def before_update(self):
        users = []
        if self.user_role == 0: # admin rights
            users = User.select().where(User.user_role == 0).execute()
        elif self.system_settings.hide_admin_account:
            users = User.select().where(User.user_role <= self.user_role, User.user_role > 0).execute()
        else:
            users = User.select().where(User.user_role <= self.user_role).execute()
        self.user_name.options = [ft.dropdown.Option(text=user.user_name, key=user.id) for user in users]

    def __on_cancel(self, e):
        self.page.close(self)
        if self.on_cancel:
            self.on_cancel(e)

    def __on_confirm(self, e):
        s = self.page.session
        user_id = self.user_name.value
        user_pwd = self.user_pwd.value
        if user_id == None or user_pwd == None:
            Toast.show_error(self.page, s.get("lang.permission.user_name_and_pwd_are_required"))
            return

        user: User = User.select().where(User.user_role <= self.user_role, User.id == user_id).first()

        if user is None:
            Toast.show_error(self.page, s.get("lang.permission.user_name_or_pwd_is_incorrect"))
            return

        if not user.check_password(user_pwd):
            Toast.show_error(self.page, s.get("lang.permission.user_name_or_pwd_is_incorrect"))
            return

        self.page.close(self)
        self.on_confirm(user)
