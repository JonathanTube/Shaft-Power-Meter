import flet as ft
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

        self.fullscreen = ft.Checkbox(
            col={"md": 6}, label=self.page.session.get("lang.setting.fullscreen"),
            label_position=ft.LabelPosition.LEFT,
            value=self.preference.fullscreen
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
                self.fullscreen,
                self.data_refresh_interval
            ]),
            col={"xs": 12})

    def __handle_system_unit_change(self, e):
        self.on_system_unit_change(int(self.system_unit.value))

    def save_data(self, user_id: int):
        if self.page is None:
            return

        # save preference
        new_theme = int(self.default_theme.value)
        self.preference.theme = new_theme

        new_language = int(self.language.value)
        self.preference.language = new_language

        new_fullscreen = self.fullscreen.value
        self.preference.fullscreen = new_fullscreen

        self.preference.system_unit = int(self.system_unit.value)
        self.preference.data_refresh_interval = int(self.data_refresh_interval.value)
        self.preference.save()

        OperationLog.create(
            user_id=user_id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.GENERAL_PREFERENCE,
            operation_content=model_to_dict(self.preference)
        )

        for item in Language.select():
            self.page.session.set(item.code, item.english if self.preference.language == 0 else item.chinese)

        self.page.window.full_screen = new_fullscreen
        theme = int(self.preference.theme)
        self.page.theme_mode = ft.ThemeMode.LIGHT if theme == 0 else ft.ThemeMode.DARK
        self.page.update()
        self.page.appbar.update()
