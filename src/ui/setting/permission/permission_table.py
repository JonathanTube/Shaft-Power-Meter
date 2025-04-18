import flet as ft
from ui.common.abstract_table import AbstractTable
from db.models.user import User


class PermissionTable(AbstractTable):
    def __init__(self):
        super().__init__(table_width=850)

    def load_total(self):
        role = self.kwargs.get("role")
        if role:
            return User.select().where(User.user_role == role).count()
        else:
            return User.select().count()

    def load_data(self):
        role = self.kwargs.get("role")
        users = User.select(
            User.id,
            User.user_name,
            User.user_pwd,
            User.user_role
        ).order_by(User.id.desc()).paginate(self.current_page, self.page_size)
        if role:
            users = users.where(User.user_role == role)

        return [[item.id, item.user_name, item.user_pwd, item.user_role] for item in users]

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

        return ft.Row(controls=[edit_button, delete_button])

    def __show_edit_user(self, e, items: list):
        self.edit_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(e.page.session.get("lang.permission.edit_user")),
            content=ft.Column(
                width=400,
                height=250,
                expand=False,
                controls=[
                    ft.TextField(
                        label=e.page.session.get("lang.permission.user_name"),
                        value=items[1]
                    ),
                    ft.TextField(
                        label=e.page.session.get("lang.permission.user_pwd"),
                        value=items[2],
                        password=True
                    ),
                    ft.Dropdown(
                        label=e.page.session.get("lang.permission.user_role"),
                        expand=True,
                        width=400,
                        value=items[3],
                        options=[
                            ft.dropdown.Option(text="Admin", key="admin"),
                            ft.dropdown.Option(text="Master", key="master"),
                            ft.dropdown.Option(text="Captain", key="captain")
                        ]
                    )
                ]
            ),
            actions=[
                ft.TextButton(e.page.session.get("lang.button.cancel"),
                              on_click=lambda e: e.page.close(self.edit_dialog)),
                ft.TextButton(e.page.session.get("lang.button.save"),
                              on_click=lambda e: e.page.close(self.edit_dialog))
            ]
        )
        self.page.open(self.edit_dialog)

    def __show_delete_user(self, e, items: list):
        self.delete_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(e.page.session.get("lang.permission.edit_user")),
            actions=[
                ft.TextButton(e.page.session.get("lang.button.cancel"),
                              on_click=lambda e: e.page.close(self.delete_dialog)),
                ft.TextButton(e.page.session.get("lang.button.save"),
                              on_click=lambda e: self.__on_confirm_delete(e, items[0]))
            ]
        )
        self.page.open(self.delete_dialog)

    def __on_confirm_delete(self, e, user_id: int):
        User.delete().where(User.id == user_id).execute()
        self.page.close(self.delete_dialog)
        self.search()

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
