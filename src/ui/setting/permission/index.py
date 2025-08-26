import logging
import flet as ft
import asyncio
import hashlib
from ui.common.permission_check import PermissionCheck
from ui.setting.permission.permission_table import PermissionTable
from ui.common.toast import Toast
from db.models.user import User
from common.global_data import gdata


class Permission(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 10
        self.op_user = None
        self.last_op_utc_date_time = gdata.configDateTime.utc
        self.on_click = self.__on_click

        self.task = None

    def __on_click(self, e):
        # 每次操作刷新时间 & 重启计时器
        self.last_op_utc_date_time = gdata.configDateTime.utc
        self.__restart_auto_lock()

    def build(self):
        if self.page and self.page.session:
            try:
                self.__create_lock_button()
                self.permission_check = PermissionCheck(
                    on_confirm=self.__on_permission_checked,
                    user_role=0
                )
            except:
                logging.exception('exception occured at Permission.build')

    def __create_lock_button(self):
        try:
            self.alignment = ft.alignment.center
            self.content = ft.TextButton(
                icon=ft.Icons.LOCK_ROUNDED,
                text="",
                style=ft.ButtonStyle(
                    icon_size=100,
                    icon_color=ft.Colors.INVERSE_SURFACE
                ),
                on_click=lambda e: self.page.open(self.permission_check)
            )
        except:
            pass

    def __on_permission_checked(self, user: User):
        try:
            if not self.page:
                return

            self.op_user = user
            self.last_op_utc_date_time = gdata.configDateTime.utc
            self.__restart_auto_lock()

            self.dropdown = ft.Dropdown(
                label=self.page.session.get("lang.permission.role"),
                width=200,
                value='-1',
                options=[
                    ft.dropdown.Option(text=self.page.session.get("lang.permission.all"), key='-1'),
                    ft.dropdown.Option(text=self.page.session.get("lang.permission.admin"), key="0", visible=self.op_user.user_role <= 0),
                    ft.dropdown.Option(text=self.page.session.get("lang.permission.master"), key="1", visible=self.op_user.user_role <= 1),
                    ft.dropdown.Option(text=self.page.session.get("lang.permission.user"), key="2", visible=self.op_user.user_role <= 2)
                ]
            )

            self.add_user_button = ft.OutlinedButton(
                text=self.page.session.get("lang.permission.add_user"),
                height=45,
                on_click=self.__on_add_user
            )
            self.permission_table = PermissionTable(user)
            self.content = ft.Column([
                ft.Row([self.dropdown, self.add_user_button]),
                self.permission_table
            ])
            self.update()
        except:
            logging.exception('exception occured at Permission.__on_permission_checked')

    def __on_add_user(self, e):
        try:
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
        except:
            logging.exception('exception occured at Permission.__on_add_user')

    def __on_add_user_confirm(self, e):
        try:
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

            if User.select().where(User.user_name == self.user_name.value.strip()).exists():
                Toast.show_warning(self.page, self.page.session.get("lang.permission.user_name_exists"))
                return

            user = User.create(
                user_name=self.user_name.value.strip(),
                user_pwd=hashlib.sha256(self.password.value.strip().encode()).hexdigest(),
                user_role=self.role.value
            )
            self.page.close(self.add_dialog)
            if self.permission_table and self.permission_table.page:
                self.permission_table.search(role=self.dropdown.value)
                self.permission_table.update()
        except:
            logging.exception('exception occured at Permission.__on_add_user_confirm')

    def __is_empty(self, value: str):
        return value == None or value.strip() == ""

    def __on_dropdown_change(self, e):
        try:
            if self.permission_table and self.permission_table.page:
                self.permission_table.search(role=e.control.value)
                self.permission_table.update()
        except:
            logging.exception('exception occured at Permission.__on_dropdown_change')
    # ---------------------
    # 自动锁定逻辑
    # ---------------------

    async def __auto_lock(self):
        try:
            await asyncio.sleep(600)  # 10分钟无操作
            # 检查是否真的超过 10 分钟
            time_diff = gdata.configDateTime.utc - self.last_op_utc_date_time
            if time_diff.total_seconds() >= 600:
                self.__create_lock_button()
                if self.page:
                    self.update()
        except asyncio.CancelledError:
            # 正常取消，不算异常
            return
        except:
            logging.exception("exception occured at Permission.__auto_lock")

    def __restart_auto_lock(self):
        if self.task:
            self.task.cancel()
        self.task = self.page.run_task(self.__auto_lock)

    # ---------------------
    # 生命周期
    # ---------------------
    def did_mount(self):
        if not gdata.configTest.auto_testing:
            self.page.open(self.permission_check)
        self.__restart_auto_lock()

    def will_unmount(self):
        if self.task:
            self.task.cancel()
            self.task = None
