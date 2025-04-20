import flet as ft
from ui.common.toast import Toast
from ui.setting.permission.permission_table import PermissionTable
from db.models.user import User


class Permission(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 10

    def build(self):
        self.dropdown = ft.Dropdown(
            label=self.page.session.get("lang.permission.role"),
            width=200,
            value=None,
            options=[
                ft.dropdown.Option(text=self.page.session.get("lang.permission.all"), key=None),
                ft.dropdown.Option(text=self.page.session.get("lang.permission.admin"), key="admin"),
                ft.dropdown.Option(text=self.page.session.get("lang.permission.master"), key="master"),
                ft.dropdown.Option(text=self.page.session.get("lang.permission.captain"), key="captain")
            ],
            on_change=self.__on_dropdown_change
        )

        self.add_user_button = ft.TextButton(
            text=self.page.session.get("lang.permission.add_user"),
            on_click=self.__on_add_user
        )
        self.permission_table = PermissionTable()
        self.content = ft.Column(
            [
                ft.Row(
                    [
                        self.dropdown,
                        self.add_user_button
                    ]
                ),
                self.permission_table
            ]
        )

    def __on_add_user(self, e):
        self.user_name = ft.TextField(
            label=e.page.session.get("lang.permission.user_name")
        )
        self.password = ft.TextField(
            label=e.page.session.get("lang.permission.user_pwd"),
            password=True
        )
        self.confirm_password = ft.TextField(
            label=e.page.session.get("lang.permission.confirm_user_pwd"),
            password=True
        )
        self.role = ft.Dropdown(
            label=e.page.session.get("lang.permission.user_role"),
            expand=True,
            width=400,
            options=[
                ft.dropdown.Option(text="Master", key="master"),
                ft.dropdown.Option(text="Captain", key="captain")
            ]
        )
        self.add_dialog = ft.AlertDialog(
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
                ft.TextButton(e.page.session.get("lang.button.cancel"),
                              on_click=lambda e: e.page.close(self.add_dialog)),
                ft.TextButton(e.page.session.get("lang.button.save"),
                              on_click=lambda e: self.__on_add_user_confirm(e))
            ]
        )
        self.page.open(self.add_dialog)

    def __on_add_user_confirm(self, e):
        if self.user_name.value.strip() == "":
            Toast.show_warning(
                e.page,
                e.page.session.get("lang.permission.user_name_required")
            )
            return

        if self.password.value.strip() == "":
            Toast.show_warning(
                e.page,
                e.page.session.get("lang.permission.user_pwd_required")
            )
            return

        if self.confirm_password.value.strip() == "":
            Toast.show_warning(
                e.page,
                e.page.session.get("lang.permission.confirm_user_pwd_required")
            )
            return

        if self.role.value.strip() == "":
            Toast.show_warning(
                e.page,
                e.page.session.get("lang.permission.user_role_required")
            )
            return

        if self.password.value.strip() != self.confirm_password.value.strip():
            Toast.show_warning(
                e.page,
                e.page.session.get("lang.permission.password_not_match")
            )
            return

        if User.select().where(User.user_name == self.user_name.value.strip()).count() > 0:
            Toast.show_warning(
                e.page,
                e.page.session.get("lang.permission.user_name_exists")
            )
            return

        User.create(
            user_name=self.user_name.value.strip(),
            user_pwd=self.password.value.strip(),
            user_role=self.role.value.strip()
        )
        self.page.close(self.add_dialog)
        self.permission_table.search(role=self.role.value)
        self.permission_table.update()

    def __on_dropdown_change(self, e):
        self.permission_table.search(role=e.control.value)
        self.permission_table.update()
