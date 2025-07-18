import flet as ft
import time
import flet as ft
import logging
from db.models.user import User
from ui.common.keyboard import keyboard
from ui.common.permission_check import PermissionCheck
from ui.common.toast import Toast
from ui.setting.system_conf.system_conf_settings import SystemConfSettings
from ui.setting.system_conf.system_conf_ship_info import SystemConfShipInfo
from ui.common.toast import Toast
from db.table_init import TableInit
from utils.system_exit_tool import SystemExitTool

class SystemConf(ft.Container):
    def __init__(self):
        super().__init__()
        self.is_saving = False

    def build(self):
        try:
            if self.page and self.page.session:
                self.system_conf_settings = SystemConfSettings()
                self.system_conf_ship_info = SystemConfShipInfo()

                self.save_button = ft.FilledButton(self.page.session.get("lang.button.save"), width=120, height=40, on_click=self.__on_save_button_click)
                self.reset_button = ft.OutlinedButton(self.page.session.get("lang.button.reset"), width=120, height=40, on_click=self.__reset_data)

                buttons = ft.Row(col={'xs': 12}, alignment=ft.MainAxisAlignment.CENTER, controls=[self.save_button, self.reset_button])

                self.content = ft.Column(
                    scroll=ft.ScrollMode.ADAPTIVE,
                    expand=True,
                    controls=[
                        ft.ResponsiveRow(
                            alignment=ft.MainAxisAlignment.START,
                            controls=[
                                self.system_conf_settings,
                                self.system_conf_ship_info,
                                buttons
                            ]
                        )
                    ])
        except:
            logging.exception('exception occured at SystemConf.build')

    def __on_save_button_click(self, e):
        try:
            if self.page is not None:
                self.page.open(PermissionCheck(self.__save_data, 0))
        except:
            logging.exception('exception occured at SystemConf.__on_save_button_click')

    def __change_buttons(self):
        try:
            if self.save_button and self.save_button.page:
                self.save_button.disabled = self.is_saving
                self.save_button.update()

            if self.reset_button and self.reset_button.page:
                self.reset_button.disabled = self.is_saving
                self.reset_button.update()
        except:
            logging.exception('exception occured at SystemConf.__change_buttons')

    def __save_data(self, user: User):
        if self.page is None:
            return

        if self.is_saving:
            return

        try:
            self.is_saving = True
            self.__change_buttons()

            keyboard.close()
            self.system_conf_settings.save(user)
            self.system_conf_ship_info.save(user)
            Toast.show_success(self.page)
            self.is_saving = False
            self.__change_buttons()
        except SystemError:
            # 退出系统
            msg = self.page.session.get("lang.toast.system_exit")
            Toast.show_error(self.page, msg, auto_hide=False)
            # 清理数据
            self.page.run_task(SystemExitTool.exit_app, self.page, user)
            time.sleep(5)
            TableInit.handle_change_running_mode()
        except:
            logging.exception("system conf save data error")
            Toast.show_error(self.page)

    def __reset_data(self, e):
        try:
            keyboard.close()
            self.content.clean()
            self.build()
            Toast.show_success(e.page)
        except:
            logging.exception("exception occured at SystemConf.__reset_data")
