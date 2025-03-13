import datetime

import flet as ft

from src.database.models.date_time_conf import DateTimeConf
from src.database.models.limitations import Limitations
from src.database.models.preference import Preference
from ..common.custom_card import create_card
from ..common.toast import Toast


class General:
    def __init__(self):
        self.last_preference = Preference.select().order_by(Preference.id.desc()).first()
        if self.last_preference is None:
            self.last_preference = Preference.create(system_unit=0, language=0, data_refresh_interval=5)

        self.last_limitations = Limitations.select().order_by(Limitations.id.desc()).first()
        if self.last_limitations is None:
            self.last_limitations = Limitations.create(
                speed_max=0, torque_max=0, power_max=0,
                speed_warning=0, torque_warning=0, power_warning=0
            )

        self.last_date_time_conf = DateTimeConf.select().order_by(DateTimeConf.id.desc()).first()
        if self.last_date_time_conf is None:
            self.last_date_time_conf = DateTimeConf.create(
                utc_date=datetime.datetime.now().date(),
                utc_time=datetime.datetime.now().time().strftime('%H:%M:%S'),
                system_date=datetime.datetime.now().date(),
                system_time=datetime.datetime.now().time().strftime('%H:%M:%S'),
                sync_with_gps=False,
                date_time_format='YYYY-MM-dd HH:mm:ss'
            )

    def __create_preference_card(self):
        self.system_unit = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="0", label="SI"),
                ft.Radio(value="1", label="Metric")
            ]),
            value=self.last_preference.system_unit,
            on_change=lambda e: setattr(self.last_preference, 'system_unit', e.control.value)
        )

        self.language = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="0", label="English"),
                ft.Radio(value="1", label="中文")
            ]),
            value=self.last_preference.language,
            on_change=lambda e: setattr(self.last_preference, 'language', e.control.value)
        )

        self.data_refresh_interval = ft.TextField(
            label="Data Refresh Interval",
            suffix_text="seconds",
            value=self.last_preference.data_refresh_interval,
            col={"md": 6},
            on_change=lambda e: setattr(self.last_preference, 'data_refresh_interval', e.control.value))

        self.preference_card = create_card(
            'Preference',
            ft.ResponsiveRow(controls=[
                ft.Row(controls=[ft.Text("System Units"), self.system_unit], col={"md": 6}),
                self.data_refresh_interval,
                ft.Row(controls=[ft.Text("Language"), self.language], col={"md": 6})
            ]),
            col={"xs": 12})

    def __create_max_limitations_card(self):
        self.speed_max = ft.TextField(
            suffix_text="rpm", label="Speed", value=self.last_limitations.speed_max,
            on_change=lambda e: setattr(self.last_limitations, 'speed_max', e.control.value)
        )

        self.torque_max = ft.TextField(
            suffix_text="kNm", label="Torque", value=self.last_limitations.torque_max,
            on_change=lambda e: setattr(self.last_limitations, 'torque_max', e.control.value)
        )

        self.power_max = ft.TextField(
            suffix_text="kW", label="Power", value=self.last_limitations.power_max,
            on_change=lambda e: setattr(self.last_limitations, 'power_max', e.control.value)
        )
        self.max_limitations_card = create_card(
            'Maximum Limitations',
            ft.Column(controls=[
                self.speed_max,
                self.torque_max,
                self.power_max
            ]))

    def __create_warning_limitations_card(self):
        self.torque_warning = ft.TextField(
            suffix_text="kNm", label="Torque", value=self.last_limitations.torque_warning,
            on_change=lambda e: setattr(self.last_limitations, 'torque_warning', e.control.value)
        )

        self.speed_warning = ft.TextField(
            suffix_text="rpm", label="Speed", value=self.last_limitations.speed_warning,
            on_change=lambda e: setattr(self.last_limitations, 'speed_warning', e.control.value)
        )

        self.power_warning = ft.TextField(
            suffix_text="kW", label="Power", value=self.last_limitations.power_warning,
            on_change=lambda e: setattr(self.last_limitations, 'power_warning', e.control.value)
        )
        self.warning_limitations_card = create_card(
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
            on_change=lambda e: self.__set_date_time('date_time_format', e.control.value)
        )

        self.sync_with_gps = ft.Switch(
            label='Sync With GPS',
            col={"md": 6},
            value=self.last_date_time_conf.sync_with_gps,
            on_change=lambda e: self.__set_date_time('sync_with_gps', e.control.value)
        )

        self.date_time_card = create_card(
            'Date And Time',
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
        Toast.show_success(e.page, message="保存成功")

    def __cancel_data(self, e):
        self.last_preference = Preference.select().order_by(Preference.id.desc()).first()
        self.last_limitations = Limitations.select().order_by(Limitations.id.desc()).first()
        self.last_date_time_conf = DateTimeConf.select().order_by(DateTimeConf.id.desc()).first()

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
        Toast.show_success(e.page, message="已取消")

    def create(self):
        self.__create_preference_card(),
        self.__create_max_limitations_card(),
        self.__create_warning_limitations_card(),
        self.__create_date_time_card(),
        return ft.Column(
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
                                ft.FilledButton(text="Save", width=120, height=40, on_click=self.__save_data),
                                ft.OutlinedButton(text="Cancel", width=120, height=40, on_click=self.__cancel_data)
                            ])
                    ])
            ])
