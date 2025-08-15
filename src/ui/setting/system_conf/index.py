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

    def __save_data(self, user: User):
        if self.page is None:
            return

        try:
            keyboard.close()

            if self.system_conf_settings and self.system_conf_settings.page:
                self.system_conf_settings.save(user)
                self.system_conf_settings.update()

            if self.system_conf_ship_info and self.system_conf_ship_info.page:
                self.system_conf_ship_info.update()
                self.system_conf_ship_info.save(user)
            # 清理数据
            TableInit.handle_change_running_mode()
            # 退出系统
            self.page.run_task(SystemExitTool.exit_app, self.page, user)
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
