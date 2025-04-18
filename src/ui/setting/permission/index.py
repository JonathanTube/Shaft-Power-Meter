import flet as ft
from ui.setting.permission.permission_table import PermissionTable


class Permission(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 10

    def build(self):
        self.dropdown = ft.Dropdown(
            label="Role",
            width=200,
            options=[
                ft.dropdown.Option(text="Admin", key="admin"),
                ft.dropdown.Option(text="Master", key="master"),
                ft.dropdown.Option(text="Captain", key="captain")
            ],
            on_change=self.__on_dropdown_change
        )
        self.permission_table = PermissionTable()
        self.content = ft.Column(
            [
                self.dropdown,
                self.permission_table
            ]
        )

    def __on_dropdown_change(self, e):
        self.permission_table.search(role=e.control.value)
        self.permission_table.update()
