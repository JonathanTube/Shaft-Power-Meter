import flet as ft
from ui.common.abstract_table import AbstractTable
from db.models.user import User
from ui.common.permission_check import PermissionCheck
from ui.common.toast import Toast
from db.models.opearation_log import OperationLog
from common.operation_type import OperationType
from common.global_data import gdata
from playhouse.shortcuts import model_to_dict


class PermissionTable(AbstractTable):
    def __init__(self):
        super().__init__()
        self.user_id = None

    def load_total(self):
        role = self.kwargs.get("role")
        role = int(role) if role else -1
        if role != -1:
            return User.select().where(User.user_role == role).count()
        else:
            return User.select().count()

    def load_data(self):
        role = self.kwargs.get("role")
        role = int(role) if role else -1
        users = User.select(
            User.id,
            User.user_name,
            User.user_pwd,
            User.user_role
        ).order_by(User.id.desc()).paginate(self.current_page, self.page_size)
        if role != -1:
            users = users.where(User.user_role == role)

        return [[item.id, item.user_name, item.user_pwd, self.__get_role_name(item.user_role)] for item in users]

    def __get_role_name(self, role: int):
        if role == 0:
            return "Admin"
        elif role == 1:
            return "Captain"
        elif role == 2:
            return "Master"
        return 'Unknown'

    def __get_role_key(self, role: int):
        if role == 'Admin':
            return 0
        elif role == 'Captain':
            return 1
        elif role == 'Master':
            return 2
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
            on_click=lambda e: self.__show_delete_user(e, items)
        )

        session = self.page.session
        edit_button.text = session.get("lang.button.edit")
        delete_button.text = session.get("lang.button.delete")
        if items[1] == "root":
            return ft.Row(controls=[edit_button])
        else:
            return ft.Row(controls=[edit_button, delete_button])

    def __show_edit_user(self, e, items: list):
        self.user_name = ft.TextField(
            label=e.page.session.get("lang.permission.user_name"),
            value=items[1],
            read_only=True
        )
        self.password = ft.TextField(
            label=e.page.session.get("lang.permission.user_pwd"),
            value=items[2],
            password=True
        )
        self.confirm_password = ft.TextField(
            label=e.page.session.get("lang.permission.confirm_user_pwd"),
            value=items[2],
            password=True
        )
        self.role = ft.Dropdown(
            label=e.page.session.get("lang.permission.user_role"),
            expand=True,
            width=400,
            value=self.__get_role_key(items[3]),
            options=[
                ft.dropdown.Option(text="Admin", key="0"),
                ft.dropdown.Option(text="Captain", key="1"),
                ft.dropdown.Option(text="Master", key="2")
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
                ft.TextButton(e.page.session.get("lang.button.save"), on_click=lambda e: self.__on_confirm_edit_permission_check(e, items[0]))
            ]
        )
        self.page.open(self.edit_dialog)

    def __on_confirm_edit_permission_check(self, e, user_id: int):
        self.user_id = user_id
        if self.__is_empty(self.user_name.value):
            Toast.show_warning(e.page, e.page.session.get("lang.permission.user_name_required"))
            return

        if self.__is_empty(self.password.value):
            Toast.show_warning(e.page, e.page.session.get("lang.permission.user_pwd_required"))
            return

        if self.__is_empty(self.confirm_password.value):
            Toast.show_warning(e.page, e.page.session.get("lang.permission.confirm_user_pwd_required"))
            return

        if self.role.value == None:
            Toast.show_warning(e.page, e.page.session.get("lang.permission.user_role_required"))
            return

        if self.password.value.strip() != self.confirm_password.value.strip():
            Toast.show_warning(e.page, e.page.session.get("lang.permission.password_not_match"))
            return
        self.page.open(PermissionCheck(self.__on_confirm_edit, 0, self.__on_confirm_edit_cancel))

    def __on_confirm_edit_cancel(self, e):
        self.page.open(self.edit_dialog)

    def __on_confirm_edit(self, op_user_id: int):
        User.update(user_pwd=self.password.value.strip(), user_role=self.role.value).where(User.id == self.user_id).execute()
        OperationLog.create(
            user_id=op_user_id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.USER_UPDATE,
            operation_content=model_to_dict(User.select(User.id, User.user_name).where(User.id == self.user_id).get())
        )

        self.page.close(self.edit_dialog)
        self.search()
        Toast.show_success(self.page)

    def __is_empty(self, value: str):
        return value == None or value.strip() == ""

    def __show_delete_user(self, e, items: list):
        self.user_id = items[0]
        self.page.open(PermissionCheck(self.__on_confirm_delete, 0))

    def __on_confirm_delete(self, op_user_id: int):
        OperationLog.create(
            user_id=op_user_id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.USER_DELETE,
            operation_content=model_to_dict(User.select(User.id, User.user_name).where(User.id == self.user_id).get())
        )
        User.delete().where(User.id == self.user_id).execute()
        self.search()
        Toast.show_success(self.page)

    def create_columns(self):
        return self.__get_language()

    def __get_language(self):
        session = self.page.session
        return [
            session.get("lang.common.no"),
            session.get("lang.permission.user_name"),
            session.get("lang.permission.user_pwd"),
            session.get("lang.permission.user_role")
        ]

    def before_update(self):
        self.update_columns(self.__get_language())
