import flet as ft
from db.models.opearation_log import OperationLog
from ui.common.permission_check import PermissionCheck
from ui.common.toast import Toast
from ui.setting.permission.permission_table import PermissionTable
from db.models.user import User
from common.operation_type import OperationType
from common.global_data import gdata
from playhouse.shortcuts import model_to_dict


class Permission(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 10
        self.op_user = None

    def build(self):
        self.permission_check = PermissionCheck(on_confirm=self.__on_permission_checked, user_role=2)

    def __on_permission_checked(self, user: User):
        self.visible = True
        self.op_user = user

        self.dropdown = ft.Dropdown(
            label=self.page.session.get("lang.permission.role"),
            width=200,
            value='-1',
            options=[
                ft.dropdown.Option(text=self.page.session.get("lang.permission.all"), key='-1'),
                ft.dropdown.Option(text=self.page.session.get("lang.permission.admin"), key="0", visible=self.op_user.user_role <= 0),
                ft.dropdown.Option(text=self.page.session.get("lang.permission.master"), key="1", visible=self.op_user.user_role <= 1),
                ft.dropdown.Option(text=self.page.session.get("lang.permission.user"), key="2", visible=self.op_user.user_role <= 2)
            ],
            on_change=self.__on_dropdown_change
        )

        self.add_user_button = ft.OutlinedButton(
            text=self.page.session.get("lang.permission.add_user"),
            height=45,
            on_click=self.__on_add_user
        )
        self.permission_table = PermissionTable(user)
        self.content = ft.Column([ft.Row([self.dropdown, self.add_user_button]), self.permission_table])
        self.update()

    def __on_add_user(self, e):
        self.user_name = ft.TextField(label=e.page.session.get("lang.permission.user_name"))
        self.password = ft.TextField(label=e.page.session.get("lang.permission.user_pwd"), password=True)
        self.confirm_password = ft.TextField(label=e.page.session.get("lang.permission.confirm_user_pwd"), password=True)
        self.role = ft.Dropdown(
            label=e.page.session.get("lang.permission.user_role"),
            expand=True,
            width=400,
            options=[
                ft.dropdown.Option(text="Admin", key=0, visible=self.op_user.user_role <= 0),
                ft.dropdown.Option(text="Master", key=1, visible=self.op_user.user_role <= 1),
                ft.dropdown.Option(text="User", key=2, visible=self.op_user.user_role <= 2),
            ]
        )
        self.add_dialog = ft.AlertDialog(
            barrier_color=ft.Colors.TRANSPARENT,
            shadow_color=ft.Colors.PRIMARY,
            title=ft.Text(e.page.session.get("lang.permission.add_user")),
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
                ft.TextButton(e.page.session.get("lang.button.cancel"), on_click=lambda e: e.page.close(self.add_dialog)),
                ft.TextButton(e.page.session.get("lang.button.save"), on_click=lambda e: self.__on_add_user_confirm(e))
            ]
        )
        self.page.open(self.add_dialog)

    def __on_add_user_confirm(self, e):
        if self.__is_empty(self.user_name.value):
            Toast.show_warning(self.page, self.page.session.get("lang.permission.user_name_required"))
            return

        if self.__is_empty(self.password.value):
            Toast.show_warning(self.page, self.page.session.get("lang.permission.user_pwd_required"))
            return

        if self.__is_empty(self.confirm_password.value):
            Toast.show_warning(self.page, self.page.session.get("lang.permission.confirm_user_pwd_required"))
            return

        if self.role.value == None:
            Toast.show_warning(self.page, self.page.session.get("lang.permission.user_role_required"))
            return

        if self.password.value.strip() != self.confirm_password.value.strip():
            Toast.show_warning(self.page, self.page.session.get("lang.permission.password_not_match"))
            return

        if User.select().where(User.user_name == self.user_name.value.strip()).count() > 0:
            Toast.show_warning(self.page, self.page.session.get("lang.permission.user_name_exists"))
            return

        user = User.create(
            user_name=self.user_name.value.strip(),
            user_pwd=self.password.value.strip(),
            user_role=self.role.value
        )
        OperationLog.create(
            user_id=self.op_user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.USER_ADD,
            operation_content=model_to_dict(User.select(User.id, User.user_name).where(User.id == user.id).get())
        )
        self.page.close(self.add_dialog)
        self.permission_table.search(role=self.dropdown.value)
        self.permission_table.update()

    def __is_empty(self, value: str):
        return value == None or value.strip() == ""

    def __on_dropdown_change(self, e):
        self.permission_table.search(role=e.control.value)
        self.permission_table.update()

    def did_mount(self):
        self.page.open(self.permission_check)
