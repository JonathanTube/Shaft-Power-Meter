import logging
import flet as ft

from common.control_manager import ControlManager
from db.models.language import Language
from ui.common.custom_card import CustomCard
from db.models.preference import Preference
from db.models.operation_log import OperationLog
from common.operation_type import OperationType
from playhouse.shortcuts import model_to_dict
from ui.common.keyboard import keyboard
from common.global_data import gdata


class GeneralPreference(ft.Container):
    def __init__(self, on_system_unit_change: callable):
        super().__init__()
        self.expand = True
        self.preference: Preference = Preference.get()
        self.on_system_unit_change = on_system_unit_change

    def build(self):
        s = self.page.session
        self.theme_label = ft.Text(s.get("lang.setting.theme"))
        self.theme_light = ft.Radio(value=0, label=s.get("lang.setting.theme.light"))
        self.theme_dark = ft.Radio(value=1, label=s.get("lang.setting.theme.dark"))

        self.language_label = ft.Text(s.get("lang.setting.language"))
        self.system_unit_label = ft.Text(s.get("lang.setting.unit"))
        self.data_refresh_interval_label = ft.Text(s.get("lang.setting.data_refresh_interval"))

        self.default_theme = ft.RadioGroup(
            content=ft.Row([self.theme_light, self.theme_dark]),
            value=self.preference.theme
        )

        self.system_unit_si = ft.Radio(value="0", label=s.get("lang.setting.unit.si"))
        self.system_unit_metric = ft.Radio(value="1", label=s.get("lang.setting.unit.metric"))

        self.system_unit = ft.RadioGroup(
            content=ft.Row([self.system_unit_si, self.system_unit_metric]),
            value=self.preference.system_unit,
            on_change=lambda e: self.__handle_system_unit_change(e)
        )

        self.language = ft.RadioGroup(
            content=ft.Row([ft.Radio(value="0", label="English"), ft.Radio(value="1", label="中文")]),
            value=self.preference.language
        )

        self.data_refresh_interval = ft.TextField(
            label=self.data_refresh_interval_label,
            suffix_text="seconds",
            value=self.preference.data_refresh_interval,
            col={"md": 6},
            read_only=True,
            can_request_focus=False,
            on_click=lambda e: keyboard.open(e.control, 'int')
        )

        self.content = CustomCard(
            self.page.session.get("lang.setting.preference"),
            ft.ResponsiveRow(controls=[
                ft.Row(controls=[self.theme_label, self.default_theme], col={"md": 6}),
                ft.Row(controls=[self.language_label, self.language], col={"md": 6}),
                ft.Row(controls=[self.system_unit_label, self.system_unit], col={"md": 6}),
                self.data_refresh_interval
            ]),
            col={"xs": 12})

    def __handle_system_unit_change(self, e):
        self.on_system_unit_change(int(self.system_unit.value))

    def save_data(self, user_id: int):
        # save preference
        new_theme = int(self.default_theme.value)
        old_theme = self.preference.theme
        self.preference.theme = new_theme

        new_language = int(self.language.value)
        old_language = self.preference.language
        self.preference.language = new_language

        self.preference.system_unit = int(self.system_unit.value)
        self.preference.data_refresh_interval = int(self.data_refresh_interval.value)
        self.preference.save()
        self.__change_theme()
        self.__refresh_language()
        OperationLog.create(
            user_id=user_id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.GENERAL_PREFERENCE,
            operation_content=model_to_dict(self.preference)
        )

        if old_theme != new_theme or old_language != new_language:
            self.__refresh_page()

    def __change_theme(self):
        theme = int(self.preference.theme)
        self.page.theme_mode = ft.ThemeMode.LIGHT if theme == 0 else ft.ThemeMode.DARK

    def __refresh_language(self):
        preference: Preference = Preference.get()
        language_items = Language.select()
        for item in language_items:
            self.page.session.set(item.code, item.english if preference.language == 0 else item.chinese)

    def __refresh_page(self):
        if ControlManager.app_bar:
            ControlManager.app_bar.clean()
            ControlManager.app_bar.build()
            ControlManager.app_bar.update()

        try:
            for control in self.page.controls:
                control.clean()
                control.build()
                control.update()
        except:
            logging.error('refresh controls of page failed.')