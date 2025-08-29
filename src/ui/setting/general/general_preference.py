import asyncio
import logging
import flet as ft
from db.models.language import Language
from db.models.preference import Preference
from ui.common.custom_card import CustomCard
from common.global_data import gdata


class GeneralPreference(ft.Container):
    def __init__(self, on_system_unit_change: callable):
        super().__init__()
        self.expand = True
        self.on_system_unit_change = on_system_unit_change

    def build(self):
        try:
            if self.page and self.page.session:
                s = self.page.session
                self.theme_label = ft.Text(s.get("lang.setting.theme"))
                self.theme_light = ft.Radio(value="0", label=s.get("lang.setting.theme.light"))
                self.theme_dark = ft.Radio(value="1", label=s.get("lang.setting.theme.dark"))

                self.language_label = ft.Text(s.get("lang.setting.language"))
                self.system_unit_label = ft.Text(s.get("lang.setting.unit"))

                self.default_theme = ft.RadioGroup(
                    content=ft.Row([self.theme_light, self.theme_dark]),
                    value=str(gdata.configPreference.theme)
                )

                self.system_unit_si = ft.Radio(value="0", label=s.get("lang.setting.unit.si"))
                self.system_unit_metric = ft.Radio(value="1", label=s.get("lang.setting.unit.metric"))

                self.system_unit = ft.RadioGroup(
                    content=ft.Row([self.system_unit_si, self.system_unit_metric]),
                    value=str(gdata.configPreference.system_unit),
                    on_change=lambda e: self.__handle_system_unit_change(e)
                )

                self.language = ft.RadioGroup(
                    content=ft.Row([ft.Radio(value="0", label="English"), ft.Radio(value="1", label="中文")]),
                    value=str(gdata.configPreference.language)
                )

                options = [
                    ft.DropdownOption(text="1s", key="1"),
                    ft.DropdownOption(text="5s", key="5"),
                    ft.DropdownOption(text="10s", key="10"),
                    ft.DropdownOption(text="60s", key="60")
                ]
                current_value = str(gdata.configPreference.data_collection_seconds_range)
                if current_value not in [opt.key for opt in options]:
                    current_value = options[0].key if options else None

                self.data_collection_seconds_range = ft.Dropdown(
                    label=s.get("lang.setting.data_collection_seconds_range"),
                    col={"md": 6},
                    expand=True,
                    width=200,
                    value=current_value,
                    options=options
                )

                self.custom_card = CustomCard(
                    self.page.session.get("lang.setting.preference"),
                    ft.ResponsiveRow(controls=[
                        ft.Row(controls=[self.theme_label, self.default_theme], col={"md": 6}),
                        ft.Row(controls=[self.language_label, self.language], col={"md": 6}),
                        ft.Row(controls=[self.system_unit_label, self.system_unit], col={"md": 6}),
                        self.data_collection_seconds_range
                    ]),
                    col={"xs": 12})
                self.content = self.custom_card
        except:
            logging.exception('exception occured at GeneralPreference.build')

    def reset(self):
        try:
            if self.page and self.page.session:
                s = self.page.session
                # 更新主题设置部分
                self.theme_label.value = s.get("lang.setting.theme")
                self.theme_light.label = s.get("lang.setting.theme.light")
                self.theme_dark.label = s.get("lang.setting.theme.dark")

                # 更新语言设置部分
                self.language_label.value = s.get("lang.setting.language")

                # 更新单位设置部分
                self.system_unit_label.value = s.get("lang.setting.unit")
                self.system_unit_si.label = s.get("lang.setting.unit.si")
                self.system_unit_metric.label = s.get("lang.setting.unit.metric")

                # 更新其他设置
                self.data_collection_seconds_range.label = s.get("lang.setting.data_collection_seconds_range")
                # 确保更新界面
                self.custom_card.set_title(s.get("lang.setting.preference"))
        except:
            logging.exception('exception occured at GeneralPreference.before_update')

    def __handle_system_unit_change(self, e):
        self.on_system_unit_change(int(self.system_unit.value))

    def save_data(self, user_id: int):
        if self.page is None or self.page.session is None:
            return

        # save preference
        theme = int(self.default_theme.value)
        language = int(self.language.value)
        system_unit = int(self.system_unit.value)
        data_collection_seconds_range = int(self.data_collection_seconds_range.value)

        Preference.update(
            theme=theme, language=language,
            system_unit=system_unit, data_collection_seconds_range=data_collection_seconds_range
        ).execute()

        gdata.configPreference.set_default_value()

        self.refresh_language()

        if self.page:
            self.page.theme_mode = ft.ThemeMode.LIGHT if theme == 0 else ft.ThemeMode.DARK
            self.page.update()

    def refresh_language(self):
        languages = Language.select()
        for item in languages:
            if gdata.configPreference.language == 0:
                self.page.session.set(item.code, item.english)
            else:
                self.page.session.set(item.code, item.chinese)

    def before_update(self):
        s = self.page.session
        # 主题
        self.theme_label.value = s.get("lang.setting.theme")
        self.theme_light.label = s.get("lang.setting.theme.light")
        self.theme_dark.label = s.get("lang.setting.theme.dark")
        # 语言
        self.language_label.value = s.get("lang.setting.language")
        # 单位
        self.system_unit_label.value = s.get("lang.setting.unit")
        self.system_unit_si.label = s.get("lang.setting.unit.si")
        self.system_unit_metric.label = s.get("lang.setting.unit.metric")
        # 数据采集间隔
        self.data_collection_seconds_range.label = s.get("lang.setting.data_collection_seconds_range")
        # 卡片标题
        self.custom_card.heading = self.page.session.get("lang.setting.preference")
