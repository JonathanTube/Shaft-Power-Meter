import datetime

import flet as ft

from db.models.date_time_conf import DateTimeConf
from db.models.language import Language
from db.models.limitations import Limitations
from db.models.preference import Preference
from ui.common.custom_card import CustomCard
from ui.common.toast import Toast


class General(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.alignment = ft.MainAxisAlignment.START

        self.last_preference = Preference.get()
        self.last_limitations = Limitations.get()
        self.last_date_time_conf = DateTimeConf.get()

    def __create_preference_card(self):
        self.theme_label = ft.Text("Theme")
        self.theme_system = ft.Radio(value=0, label="System")
        self.theme_light = ft.Radio(value=1, label="Light")
        self.theme_dark = ft.Radio(value=2, label="Dark")

        self.language_label = ft.Text("Language")
        self.system_unit_label = ft.Text("System Unit")
        self.data_refresh_interval_label = ft.Text("Data Refresh Interval")

        self.theme = ft.RadioGroup(
            content=ft.Row([
                self.theme_system,
                self.theme_light,
                self.theme_dark
            ]),
            value=self.last_preference.theme,
            on_change=lambda e: setattr(
                self.last_preference, 'theme', e.control.value)
        )

        self.system_unit_si = ft.Radio(value="0", label="SI")
        self.system_unit_metric = ft.Radio(value="1", label="Metric")

        self.system_unit = ft.RadioGroup(
            content=ft.Row([
                self.system_unit_si,
                self.system_unit_metric
            ]),
            value=self.last_preference.system_unit,
            on_change=lambda e: setattr(
                self.last_preference, 'system_unit', e.control.value)
        )

        self.language = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="0", label="English"),
                ft.Radio(value="1", label="中文")
            ]),
            value=self.last_preference.language,
            on_change=lambda e: setattr(
                self.last_preference, 'language', e.control.value)
        )

        self.data_refresh_interval = ft.TextField(
            label=self.data_refresh_interval_label,
            suffix_text="seconds",
            value=self.last_preference.data_refresh_interval,
            col={"md": 6},
            on_change=lambda e: setattr(self.last_preference, 'data_refresh_interval', e.control.value))

        self.preference_card = CustomCard(
            'Preference',
            ft.ResponsiveRow(
                controls=[
                    ft.Row(
                        controls=[self.theme_label, self.theme],
                        col={"md": 6}
                    ),
                    ft.Row(
                        controls=[self.language_label, self.language],
                        col={"md": 6}),
                    ft.Row(
                        controls=[self.system_unit_label, self.system_unit],
                        col={"md": 6}
                    ),
                    self.data_refresh_interval
                ]),
            col={"xs": 12})

    def __create_max_limitations_card(self):
        self.speed_max = ft.TextField(
            suffix_text="rpm", label="Speed", value=self.last_limitations.speed_max,
            on_change=lambda e: setattr(
                self.last_limitations, 'speed_max', e.control.value)
        )

        self.torque_max = ft.TextField(
            suffix_text="kNm", label="Torque", value=self.last_limitations.torque_max,
            on_change=lambda e: setattr(
                self.last_limitations, 'torque_max', e.control.value)
        )

        self.power_max = ft.TextField(
            suffix_text="kW", label="Power", value=self.last_limitations.power_max,
            on_change=lambda e: setattr(
                self.last_limitations, 'power_max', e.control.value)
        )
        self.max_limitations_card = CustomCard(
            'Maximum Limitations',
            ft.Column(controls=[
                self.speed_max,
                self.torque_max,
                self.power_max
            ]))

    def __create_warning_limitations_card(self):
        self.torque_warning = ft.TextField(
            suffix_text="kNm", label="Torque", value=self.last_limitations.torque_warning,
            on_change=lambda e: setattr(
                self.last_limitations, 'torque_warning', e.control.value)
        )

        self.speed_warning = ft.TextField(
            suffix_text="rpm", label="Speed", value=self.last_limitations.speed_warning,
            on_change=lambda e: setattr(
                self.last_limitations, 'speed_warning', e.control.value)
        )

        self.power_warning = ft.TextField(
            suffix_text="kW", label="Power", value=self.last_limitations.power_warning,
            on_change=lambda e: setattr(
                self.last_limitations, 'power_warning', e.control.value)
        )
        self.warning_limitations_card = CustomCard(
            'Warning Limitations',
            ft.Column(controls=[
                self.speed_warning,
                self.torque_warning,
                self.power_warning
            ]))

    def __handle_date_change(self, e):
        utc_date = e.control.value.strftime('%Y-%m-%d')
        self.utc_date.value = utc_date
        self.utc_date.update()
        self.last_date_time_conf.utc_date = utc_date

    def __handle_time_change(self, e):
        utc_time = e.control.value.strftime('%H:%M:%S')
        self.utc_time.value = utc_time
        self.utc_time.update()
        self.last_date_time_conf.utc_time = utc_time

    def __set_date_time(self, name: str, value: str):
        if name == 'date_time_format':
            self.last_date_time_conf.date_time_format = value
        elif name == 'sync_with_gps':
            self.last_date_time_conf.sync_with_gps = value

    def __create_date_time_card(self):
        self.utc_date = ft.TextField(
            label="Date",
            col={"md": 6},
            value=self.last_date_time_conf.utc_date,
            on_click=lambda e: e.page.open(ft.DatePicker(on_change=self.__handle_date_change)))

        self.utc_time = ft.TextField(
            label="Time",
            col={"md": 6},
            value=self.last_date_time_conf.utc_time,
            on_click=lambda e: e.page.open(ft.TimePicker(on_change=self.__handle_time_change)))

        self.date_time_format = ft.Dropdown(
            label="Date Time Format", col={"md": 6},
            value=self.last_date_time_conf.date_time_format,
            options=[ft.DropdownOption(key="YYYY-MM-dd HH:mm:ss"),
                     ft.DropdownOption(key="YYYY/MM/dd HH:mm:ss"),
                     ft.DropdownOption(key="dd/MM/YYYY HH:mm:ss"),
                     ft.DropdownOption(key="MM/dd/YYYY HH:mm:ss")],
            on_change=lambda e: self.__set_date_time(
                'date_time_format', e.control.value)
        )

        self.sync_with_gps = ft.Switch(
            label='Sync With GPS',
            col={"md": 6},
            value=self.last_date_time_conf.sync_with_gps,
            on_change=lambda e: self.__set_date_time(
                'sync_with_gps', e.control.value)
        )

        self.date_time_card = CustomCard(
            'UTC Date Time Conf.',
            ft.ResponsiveRow(
                controls=[
                    self.utc_date,
                    self.utc_time,
                    self.date_time_format,
                    self.sync_with_gps
                ]
            ),
            col={"xs": 12}
        )

    def __save_data(self, e):
        self.last_preference.save()
        self.last_limitations.save()
        self.last_date_time_conf.save()
        Toast.show_success(e.page)
        self.__refresh_language(e.page)
        self.__change_theme(e.page)
        e.page.update()

    def __change_theme(self, page: ft.Page):
        if self.last_preference.theme == '1':
            page.theme_mode = ft.ThemeMode.LIGHT
        elif self.last_preference.theme == '2':
            page.theme_mode = ft.ThemeMode.DARK
        else:
            page.theme_mode = ft.ThemeMode.SYSTEM

    def __refresh_language(self, page: ft.Page):
        language_items = Language.select()

        if Preference.get().language == 0:
            for item in language_items:
                page.session.set(item.code, item.english)
        else:
            for item in language_items:
                page.session.set(item.code, item.chinese)

    def __cancel_data(self, e):
        self.last_preference = Preference.select().order_by(Preference.id.desc()).first()
        self.last_limitations = Limitations.select().order_by(Limitations.id.desc()).first()
        self.last_date_time_conf = DateTimeConf.select().order_by(
            DateTimeConf.id.desc()).first()

        self.system_unit.value = self.last_preference.system_unit
        self.language.value = self.last_preference.language
        self.data_refresh_interval.value = self.last_preference.data_refresh_interval
        self.preference_card.update()

        self.speed_max.value = self.last_limitations.speed_max
        self.power_max.value = self.last_limitations.power_max
        self.torque_max.value = self.last_limitations.torque_max
        self.max_limitations_card.update()

        self.speed_warning.value = self.last_limitations.speed_warning
        self.power_warning.value = self.last_limitations.power_warning
        self.torque_warning.value = self.last_limitations.torque_warning
        self.warning_limitations_card.update()

        self.utc_date.value = self.last_date_time_conf.utc_date
        self.utc_time.value = self.last_date_time_conf.utc_time
        self.date_time_format.value = self.last_date_time_conf.date_time_format
        self.sync_with_gps.value = self.last_date_time_conf.sync_with_gps
        self.date_time_card.update()
        Toast.show_success(e.page)

    def build(self):
        self.__create_preference_card()
        self.__create_max_limitations_card()
        self.__create_warning_limitations_card()
        self.__create_date_time_card()

        self.save_button = ft.FilledButton(
            text="Save",
            width=120, height=40,
            on_click=self.__save_data
        )
        self.cancel_button = ft.OutlinedButton(
            text="Cancel",
            width=120, height=40,
            on_click=self.__cancel_data
        )

        self.content = ft.Column(
            expand=True,
            controls=[
                ft.ResponsiveRow(
                    controls=[
                        self.preference_card,
                        self.max_limitations_card,
                        self.warning_limitations_card,
                        self.date_time_card,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                self.save_button,
                                self.cancel_button
                            ])
                    ]
                )
            ]
        )

    def before_update(self):
        self.__set_language()

    def did_mount(self):
        self.__set_language()

    def __set_language(self):
        session = self.page.session

        self.preference_card.set_title(session.get("lang.setting.preference"))
        self.theme_label.value = session.get("lang.setting.theme")

        self.theme_system.label = session.get("lang.setting.theme.system")
        self.theme_light.label = session.get("lang.setting.theme.light")
        self.theme_dark.label = session.get("lang.setting.theme.dark")

        self.language_label.value = session.get("lang.setting.language")
        self.system_unit_label.value = session.get("lang.setting.unit")
        self.system_unit_label.value = session.get("lang.setting.unit")
        self.system_unit_si.label = session.get("lang.setting.unit.si")
        self.system_unit_metric.label = session.get("lang.setting.unit.metric")

        self.data_refresh_interval_label.value = session.get(
            "lang.setting.data_refresh_interval")

        self.max_limitations_card.set_title(
            session.get("lang.setting.maximum_limitations"))

        self.warning_limitations_card.set_title(
            session.get("lang.setting.warning_limitations"))

        self.date_time_card.set_title(
            session.get("lang.setting.utc_date_time_conf"))

        self.utc_date.label = session.get("lang.setting.date")
        self.utc_time.label = session.get("lang.setting.time")
        self.date_time_format.label = session.get(
            "lang.setting.date_time_format")
        self.sync_with_gps.label = session.get("lang.setting.sync_with_gps")

        self.speed_max.label = session.get("lang.common.speed")
        self.torque_max.label = session.get("lang.common.torque")
        self.power_max.label = session.get("lang.common.power")

        self.speed_warning.label = session.get("lang.common.speed")
        self.torque_warning.label = session.get("lang.common.torque")
        self.power_warning.label = session.get("lang.common.power")

        self.save_button.text = session.get("lang.button.save")
        self.cancel_button.text = session.get("lang.button.cancel")
