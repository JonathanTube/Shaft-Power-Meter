import flet as ft
import logging
from common.control_manager import ControlManager
from db.models.user import User
from ui.common.keyboard import keyboard
from ui.common.permission_check import PermissionCheck
from ui.common.toast import Toast
from ui.setting.system_conf.system_conf_settings import SystemConfSettings
from ui.setting.system_conf.system_conf_ship_info import SystemConfShipInfo


class SystemConf(ft.Container):
    def __init__(self):
        super().__init__()
        self.is_saving = False

    def build(self):
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

    def __on_save_button_click(self, e):
        self.page.open(PermissionCheck(self.__save_data, 0))

    def __change_buttons(self):
        if self.save_button and self.save_button.page:
            self.save_button.disabled = self.is_saving
            self.save_button.update()

        if self.reset_button and self.reset_button.page:
            self.reset_button.disabled = self.is_saving
            self.reset_button.update()

    def __save_data(self, user: User):
        if self.page is None:
            return

        if self.is_saving:
            return

        try:
            self.is_saving = True
            self.__change_buttons()

            keyboard.close()
            self.system_conf_settings.save(user.id)
            self.system_conf_ship_info.save(user.id)
            Toast.show_success(self.page)
        except:
            logging.exception("system conf save data error")
            Toast.show_error(self.page)
        finally:
            self.is_saving = False
            self.__change_buttons()

    def __reset_data(self, e):
        keyboard.close()
        self.content.clean()
        self.build()
        Toast.show_success(e.page)
