import logging
import flet as ft
import hashlib
import asyncio
from ui.common.abstract_table import AbstractTable
from db.models.user import User
from ui.common.toast import Toast
from common.global_data import gdata
from peewee import fn


class PermissionTable(AbstractTable):
    def __init__(self, user: User):
        super().__init__()
        self.op_user = user
        self.table_width = gdata.configCommon.default_table_width - 150

    async def load_total_async(self):
        role = self.kwargs.get("role")
        role = int(role) if role else -1

        def _query():
            q = User.select(fn.COUNT(User.id)).where(User.user_role >= self.op_user.user_role)
            if role != -1:
                q = q.where(User.user_role == role)
            return q.scalar() or 0
        return await asyncio.to_thread(_query)

    def load_total(self):
        # 直接同步查询，避免在 UI 线程中调用 asyncio.run
        role = self.kwargs.get("role")
        role = int(role) if role else -1
        q = User.select(fn.COUNT(User.id)).where(User.user_role >= self.op_user.user_role)
        if role != -1:
            q = q.where(User.user_role == role)
        return q.scalar() or 0

    async def load_data_async(self):
        role = self.kwargs.get("role")
        role = int(role) if role else -1

        def _query():
            q = User.select(
                User.id,
                User.user_name,
                User.user_pwd,
                User.user_role
            ).where(User.user_role >= self.op_user.user_role).order_by(User.id.desc()).paginate(self.current_page, self.page_size)
            if role != -1:
                q = q.where(User.user_role == role)
            return [[item.id, item.user_name, '******', self.__get_role_name(item.user_role)] for item in q]
        return await asyncio.to_thread(_query)

    def load_data(self):
        # 直接同步查询，避免在 UI 线程中调用 asyncio.run
        role = self.kwargs.get("role")
        role = int(role) if role else -1
        q = User.select(
            User.id,
            User.user_name,
            User.user_pwd,
            User.user_role
        ).where(User.user_role >= self.op_user.user_role).order_by(User.id.desc()).paginate(self.current_page, self.page_size)
        if role != -1:
            q = q.where(User.user_role == role)
        return [[item.id, item.user_name, '******', self.__get_role_name(item.user_role)] for item in q]

    def __get_role_name(self, role: int):
        if role == 0:
            return "Admin"
        elif role == 1:
            return "Master"
        elif role == 2:
            return "User"
        return 'Unknown'

    def __get_role_key(self, role_label: str):
        if role_label == 'Admin':
            return "0"
        elif role_label == 'Master':
            return "1"
        elif role_label == 'User':
            return "2"
        return None

    def has_operations(self):
        return True

    def create_operations(self, items: list):
        edit_button = ft.TextButton(
            icon=ft.Icons.EDIT_OUTLINED,
            text="Edit",
            on_click=lambda e: self.__show_edit_user(e, items)
        )

        delete_button = ft.TextButton(
            icon=ft.Icons.DELETE_OUTLINED,
            text="Delete",
            on_click=lambda e: self.__on_delete(e, items[0])
        )

        session = self.page.session
        edit_button.text = session.get("lang.button.edit")
        delete_button.text = session.get("lang.button.delete")
        if items[1] == "admin":
            return ft.Row(controls=[edit_button])
        else:
            return ft.Row(controls=[edit_button, delete_button])

    def __show_edit_user(self, e, items: list):
        try:
            self.user_name = ft.TextField(
                label=e.page.session.get("lang.permission.user_name"),
                value=items[1],
                read_only=True
            )
            self.password = ft.TextField(
                label=e.page.session.get("lang.permission.user_pwd"),
                value="",
                password=True,
                can_reveal_password=True
            )
            self.confirm_password = ft.TextField(
                label=e.page.session.get("lang.permission.confirm_user_pwd"),
                value="",
                password=True,
                can_reveal_password=True
            )
            current_role_key = self.__get_role_key(items[3])
            self.role = ft.Dropdown(
                label=e.page.session.get("lang.permission.user_role"),
                expand=True,
                width=400,
                value=current_role_key if current_role_key is not None else None,
                options=[
                    ft.dropdown.Option(text="Admin", key="0", visible=self.op_user.user_role <= 0),
                    ft.dropdown.Option(text="Master", key="1", visible=self.op_user.user_role <= 1),
                    ft.dropdown.Option(text="User", key="2", visible=self.op_user.user_role <= 2)
                ]
            )
            self.edit_dialog = ft.AlertDialog(
                barrier_color=ft.Colors.TRANSPARENT,
                shadow_color=ft.Colors.PRIMARY,
                title=ft.Text(e.page.session.get("lang.permission.edit_user")),
                content=ft.Column(
                    width=400,
                    height=250,
                    expand=False,
                    controls=[
                        self.user_name,
                        self.password,
                        self.confirm_password,
                        self.role
                    ]
                ),
                actions=[
                    ft.TextButton(e.page.session.get("lang.button.cancel"), on_click=lambda e: e.page.close(self.edit_dialog)),
                    ft.TextButton(e.page.session.get("lang.button.save"), on_click=lambda e: self.__on_confirm_edit_async(e, items[0]))
                ]
            )
            self.page.open(self.edit_dialog)
        except:
            logging.exception('exception occured at PermissionTable.__show_edit_user')

    def __on_confirm_edit_async(self, e, user_id: int):
        try:
            if self.__is_empty(self.user_name.value):
                Toast.show_warning(e.page, e.page.session.get("lang.permission.user_name_required"))
                return

            if self.__is_empty(self.password.value):
                Toast.show_warning(e.page, e.page.session.get("lang.permission.user_pwd_required"))
                return

            if self.__is_empty(self.confirm_password.value):
                Toast.show_warning(e.page, e.page.session.get("lang.permission.confirm_user_pwd_required"))
                return

            if self.role.value is None:
                Toast.show_warning(e.page, e.page.session.get("lang.permission.user_role_required"))
                return

            if self.password.value.strip() != self.confirm_password.value.strip():
                Toast.show_warning(e.page, e.page.session.get("lang.permission.password_not_match"))
                return

            encrypt_password = hashlib.sha256(self.password.value.strip().encode()).hexdigest()

            User.update(
                user_pwd=encrypt_password,
                user_role=int(self.role.value)
            ).where(User.id == user_id).execute()

            self.page.close(self.edit_dialog)
            self.search()
            Toast.show_success(self.page)
        except:
            logging.exception('exception occured at PermissionTable.__on_confirm_edit')

    def __is_empty(self, value: str):
        return value is None or value.strip() == ""

    def __on_delete(self, e, user_id: int):
        try:
            self.del_dialog = ft.AlertDialog(
                title=ft.Text(self.page.session.get("lang.permission.delete_user")),
                actions=[
                    ft.TextButton(self.page.session.get("lang.button.cancel"), on_click=lambda e: e.page.close(self.del_dialog)),
                    ft.TextButton(self.page.session.get("lang.button.confirm"), on_click=lambda e: self.__on_delete_confirm_async(e, user_id))
                ]
            )
            self.page.open(self.del_dialog)
        except:
            logging.exception('exception occured at PermissionTable.__on_delete')

    def __on_delete_confirm_async(self, e, user_id: int):
        try:
            self.page.close(self.del_dialog)

            User.delete().where(User.id == user_id).execute()
            self.search()
            Toast.show_success(self.page)
        except:
            logging.exception('exception occured at PermissionTable.__on_delete_confirm')

    def create_columns(self):
        session = self.page.session
        return [
            session.get("lang.common.no"),
            session.get("lang.permission.user_name"),
            session.get("lang.permission.user_pwd"),
            session.get("lang.permission.user_role")
        ]
