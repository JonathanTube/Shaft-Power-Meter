import flet as ft
import logging
from ui.setting.general.general_limitation_max import GeneralLimitationMax
from ui.setting.general.general_date_time import GeneralDateTime
from ui.setting.general.general_limitation_warning import GeneralLimitationWarning
from ui.setting.general.general_preference import GeneralPreference
from ui.common.toast import Toast
from ui.common.permission_check import PermissionCheck
from ui.common.keyboard import keyboard
from db.models.user import User
from ui.setting.general.general_ofline_default_value import GeneralOflineDefaultValue
from common.global_data import gdata


class General(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.system_unit = gdata.configPreference.system_unit
        self.is_saving = False

    def __on_save_button_click(self, e):
        try:
            keyboard.close()
            if self.page is not None:
                self.page.open(PermissionCheck(self.__save_data, 2))
        except:
            logging.exception('exception occured at General.__on_save_button_click')

    def __on_system_unit_change(self, system_unit: int):
        self.system_unit = system_unit
        self.limitation_max.update_unit(system_unit)
        self.limitation_warning.update_unit(system_unit)
        self.general_offline_default_value.update_unit(system_unit)

    def build(self):
        try:
            if self.page and self.page.session:
                self.general_preference = GeneralPreference(self.__on_system_unit_change)
                self.limitation_max = GeneralLimitationMax(self.system_unit)
                self.limitation_warning = GeneralLimitationWarning(self.system_unit)
                self.general_date_time = GeneralDateTime()
                self.general_offline_default_value = GeneralOflineDefaultValue(self.system_unit)

                self.save_btn = ft.FilledButton(self.page.session.get("lang.button.save"), width=120, height=40, on_click=lambda e: self.__on_save_button_click(e))
                self.reset_btn = ft.OutlinedButton(self.page.session.get("lang.button.reset"), width=120, height=40, on_click=lambda e: self.__reset_data(e))

                self.content = ft.Column(
                    scroll=ft.ScrollMode.ADAPTIVE,
                    expand=True,
                    controls=[
                        ft.ResponsiveRow(
                            controls=[
                                self.general_preference,
                                self.limitation_max,
                                self.limitation_warning,
                                self.general_offline_default_value,
                                self.general_date_time,
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        self.save_btn,
                                        self.reset_btn
                                    ])
                            ]
                        )
                    ]
                )
        except:
            logging.exception('exception occured at General.build')

    def __change_buttons(self):
        if self.save_btn and self.save_btn.page:
            self.save_btn.disabled = self.is_saving
            self.save_btn.update()

        if self.reset_btn and self.reset_btn.page:
            self.reset_btn.disabled = self.is_saving
            self.reset_btn.update()

    def __save_data(self, user: User):
        if self.page is None:
            return

        if self.is_saving:
            return

        try:
            self.is_saving = True
            self.__change_buttons()

            if self.save_btn and self.save_btn.page:
                self.save_btn.disabled = True
                self.save_btn.update()

            if self.reset_btn and self.reset_btn.page:
                self.reset_btn.disabled = True
                self.reset_btn.update()

            user_id = user.id
            self.general_preference.save_data(user_id)
            self.limitation_max.save_data(user_id)
            self.limitation_warning.save_data(user_id)
            self.general_offline_default_value.save_data(user_id)
            self.general_date_time.save_data(user_id)
            Toast.show_success(self.page)
        except:
            logging.exception("general save data error")
            Toast.show_error(self.page)
        finally:
            self.is_saving = False
            self.__change_buttons()

    def __reset_data(self, e):
        try:
            if self.page:
                keyboard.close()
                if self.general_date_time and self.general_date_time.page:
                    self.general_date_time.reset()
                    self.general_date_time.update()

                if self.limitation_max and self.limitation_max.page:
                    self.limitation_max.reset()
                    self.limitation_max.update()

                if self.limitation_warning and self.limitation_warning.page:
                    self.limitation_warning.reset()
                    self.limitation_warning.update()

                if self.general_offline_default_value and self.general_offline_default_value.page:
                    self.general_offline_default_value.reset()
                    self.general_offline_default_value.update()

                if self.general_preference and self.general_preference.page:
                    self.general_preference.reset()
                    self.general_preference.update()

        except:
            logging.exception('exception occured at General.__reset_data')
