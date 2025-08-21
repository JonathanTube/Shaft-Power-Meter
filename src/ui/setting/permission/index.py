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
                ],
                on_change=self.__on_dropdown_change
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
