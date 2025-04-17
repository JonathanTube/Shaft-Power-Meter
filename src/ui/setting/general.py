import flet as ft
import asyncio
from datetime import datetime
from db.models.date_time_conf import DateTimeConf
from db.models.language import Language
from db.models.limitations import Limitations
from db.models.preference import Preference
from ui.common.custom_card import CustomCard
from ui.common.toast import Toast
from utils.unit_converter import UnitConverter


reg_digital = r'^(\d+\.?\d*|)$'  # 允许整数、小数或空字符串


class General(ft.Container):
    def __init__(self):
        super().__init__()
        self._task = None

        self.expand = True
        self.alignment = ft.MainAxisAlignment.START

        self.last_preference = Preference.get()
        self.last_limitations = Limitations.get()
        self.last_date_time_conf = DateTimeConf.get()

    def __create_preference_card(self):
        self.theme_label = ft.Text(self.page.session.get("lang.setting.theme"))
        self.theme_system = ft.Radio(value=0, label=self.page.session.get("lang.setting.theme.system"))
        self.theme_light = ft.Radio(value=1, label=self.page.session.get("lang.setting.theme.light"))
        self.theme_dark = ft.Radio(value=2, label=self.page.session.get("lang.setting.theme.dark"))

        self.language_label = ft.Text(self.page.session.get("lang.setting.language"))
        self.system_unit_label = ft.Text(self.page.session.get("lang.setting.unit"))
        self.data_refresh_interval_label = ft.Text(self.page.session.get("lang.setting.data_refresh_interval"))

        self.theme = ft.RadioGroup(
            content=ft.Row(
                [self.theme_system, self.theme_light, self.theme_dark]),
            value=self.last_preference.theme
        )

        self.system_unit_si = ft.Radio(value="0", label=self.page.session.get("lang.setting.unit.si"))
        self.system_unit_metric = ft.Radio(value="1", label=self.page.session.get("lang.setting.unit.metric"))

        self.system_unit = ft.RadioGroup(
            content=ft.Row([
                self.system_unit_si,
                self.system_unit_metric
            ]),
            value=self.last_preference.system_unit,
            on_change=lambda e: self.__handle_system_unit_change(e)
        )

        self.language = ft.RadioGroup(
            content=ft.Row([
                ft.Radio(value="0", label="English"),
                ft.Radio(value="1", label="中文")
            ]),
            value=self.last_preference.language
        )

        self.data_refresh_interval = ft.TextField(
            label=self.data_refresh_interval_label,
            suffix_text="seconds",
            value=self.last_preference.data_refresh_interval,
            col={"md": 6}
        )

        self.preference_card = CustomCard(
            self.page.session.get("lang.setting.preference"),
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

    def __handle_system_unit_change(self, e):
        self.__update_limitations()

    def __create_max_limitations_card(self):
        self.speed_max = ft.TextField(
            suffix_text="rpm", label=self.page.session.get("lang.common.speed"), value=self.last_limitations.speed_max,
            input_filter=ft.InputFilter(regex_string=reg_digital)
        )

        self.torque_max = ft.TextField(
            suffix_text="kNm", label=self.page.session.get("lang.common.torque"), value=self.last_limitations.torque_max,
            input_filter=ft.InputFilter(regex_string=reg_digital)
        )

        self.power_max = ft.TextField(
            suffix_text="kW", label=self.page.session.get("lang.common.power"), value=self.last_limitations.power_max,
            input_filter=ft.InputFilter(regex_string=reg_digital)
        )

        self.max_limitations_card = CustomCard(
            self.page.session.get("lang.setting.maximum_limitations"),
            ft.Column(controls=[
                self.speed_max,
                self.torque_max,
                self.power_max
            ]))

    def __create_warning_limitations_card(self):
        self.torque_warning = ft.TextField(
            suffix_text="kNm", label=self.page.session.get("lang.common.torque"), value=self.last_limitations.torque_warning,
            input_filter=ft.InputFilter(regex_string=reg_digital)
        )

        self.speed_warning = ft.TextField(
            suffix_text="rpm", label=self.page.session.get("lang.common.speed"), value=self.last_limitations.speed_warning,
            input_filter=ft.InputFilter(regex_string=reg_digital)
        )

        self.power_warning = ft.TextField(
            suffix_text="kW", label=self.page.session.get("lang.common.power"), value=self.last_limitations.power_warning,
            input_filter=ft.InputFilter(regex_string=reg_digital)
        )

        self.warning_limitations_card = CustomCard(
            self.page.session.get("lang.setting.warning_limitations"),
            ft.Column(controls=[
                self.speed_warning,
                self.torque_warning,
                self.power_warning
            ]))

    def __update_limitations(self):
        system_unit = int(self.system_unit.value)

        torque_limit = self.last_limitations.torque_max
        power_limit = self.last_limitations.power_max

        torque_warning = self.last_limitations.torque_warning
        power_warning = self.last_limitations.power_warning
        if system_unit == 0:
            self.torque_max.suffix_text = "kNm"
            self.torque_max.value = round(torque_limit / 1000, 1)

            self.power_max.suffix_text = "kW"
            self.power_max.value = round(power_limit / 1000, 1)

            self.torque_warning.suffix_text = "kNm"
            self.torque_warning.value = round(torque_warning / 1000, 1)

            self.power_warning.suffix_text = "kW"
            self.power_warning.value = round(power_warning / 1000, 1)

        elif system_unit == 1:
            self.torque_max.suffix_text = "Tm"
            self.torque_max.value = UnitConverter.nm_to_tm(torque_limit)

            self.power_max.suffix_text = "shp"
            self.power_max.value = UnitConverter.w_to_shp(power_limit)

            self.torque_warning.suffix_text = "Tm"
            self.torque_warning.value = UnitConverter.nm_to_tm(torque_warning)

            self.power_warning.suffix_text = "shp"
            self.power_warning.value = UnitConverter.w_to_shp(power_warning)

        self.max_limitations_card.update()
        self.warning_limitations_card.update()

    def __handle_date_change(self, e):
        utc_date = e.control.value.strftime('%Y-%m-%d')
        self.utc_date.value = utc_date
        self.utc_date.update()

    def __handle_time_change(self, e):
        utc_time = e.control.value.strftime('%H:%M')
        self.utc_time.value = utc_time
        self.utc_time.update()

    def __create_date_time_card(self):
        utc_date_time = self.page.session.get('utc_date_time')
        self.utc_date_time = ft.TextField(
            label=self.page.session.get("lang.setting.current_utc_date_time"),
            col={"md": 12},
            read_only=True,
            can_request_focus=False,
            value=utc_date_time.strftime('%Y-%m-%d %H:%M')
        )

        self.utc_date = ft.TextField(
            label=self.page.session.get("lang.setting.date"),
            col={"md": 6},
            can_request_focus=False,
            value=self.last_date_time_conf.utc_date,
            on_click=lambda e: e.page.open(
                ft.DatePicker(
                    on_change=self.__handle_date_change,
                    current_date=self.last_date_time_conf.utc_date
                )
            )
        )

        self.utc_time = ft.TextField(
            label=self.page.session.get("lang.setting.time"),
            col={"md": 6},
            can_request_focus=False,
            value=self.last_date_time_conf.utc_time.strftime('%H:%M'),
            on_click=lambda e: e.page.open(
                ft.TimePicker(
                    on_change=self.__handle_time_change
                )
            )
        )

        self.date_time_format = ft.Dropdown(
            label=self.page.session.get("lang.setting.date_time_format"), col={"md": 6},
            value=self.last_date_time_conf.date_time_format,
            options=[ft.DropdownOption(key="YYYY-MM-dd HH:mm:ss"),
                     ft.DropdownOption(key="YYYY/MM/dd HH:mm:ss"),
                     ft.DropdownOption(key="dd/MM/YYYY HH:mm:ss"),
                     ft.DropdownOption(key="MM/dd/YYYY HH:mm:ss")]
        )

        self.sync_with_gps = ft.Switch(
            label=self.page.session.get("lang.setting.sync_with_gps"),
            col={"md": 6},
            value=self.last_date_time_conf.sync_with_gps
        )

        self.date_time_card = CustomCard(
            self.page.session.get("lang.setting.utc_date_time_conf"),
            ft.ResponsiveRow(
                controls=[
                    self.utc_date_time,
                    self.utc_date,
                    self.utc_time,
                    self.date_time_format,
                    self.sync_with_gps
                ]
            ),
            col={"xs": 12}
        )

    def __save_data(self, e):
        # save preference
        self.last_preference.theme = self.theme.value
        self.last_preference.system_unit = int(self.system_unit.value)
        self.last_preference.language = int(self.language.value)
        self.last_preference.data_refresh_interval = int(
            self.data_refresh_interval.value)
        self.last_preference.save()

        # save limitations
        max_speed = float(self.speed_max.value or 0)
        self.last_limitations.speed_max = max_speed
        max_torque = float(self.torque_max.value or 0)
        self.last_limitations.torque_max = max_torque
        max_power = float(self.power_max.value or 0)
        self.last_limitations.power_max = max_power

        warning_speed = float(self.speed_warning.value or 0)
        self.last_limitations.speed_warning = warning_speed
        warning_torque = float(self.torque_warning.value or 0)
        self.last_limitations.torque_warning = warning_torque
        warning_power = float(self.power_warning.value or 0)
        self.last_limitations.power_warning = warning_power

        if self.last_preference.system_unit == 0:
            # kNm to Nm
            self.last_limitations.torque_max = UnitConverter.knm_to_nm(
                max_torque)
            self.last_limitations.torque_warning = UnitConverter.knm_to_nm(
                warning_torque)
            # kw to w
            self.last_limitations.power_max = UnitConverter.kw_to_w(max_power)
            self.last_limitations.power_warning = UnitConverter.kw_to_w(
                warning_power)
        elif self.last_preference.system_unit == 1:
            # Tm to Nm
            self.last_limitations.torque_max = UnitConverter.tm_to_nm(
                max_torque)
            self.last_limitations.torque_warning = UnitConverter.tm_to_nm(
                warning_torque)
            # shp to w
            self.last_limitations.power_max = UnitConverter.shp_to_w(max_power)
            self.last_limitations.power_warning = UnitConverter.shp_to_w(
                warning_power)
        self.last_limitations.save()

        # save date time conf
        new_date = self.utc_date.value
        self.last_date_time_conf.utc_date = new_date

        new_time = self.utc_time.value
        self.last_date_time_conf.utc_time = new_time

        self.last_date_time_conf.system_date = datetime.now().date()
        self.last_date_time_conf.system_time = datetime.now().time()

        self.last_date_time_conf.date_time_format = self.date_time_format.value
        self.last_date_time_conf.sync_with_gps = self.sync_with_gps.value
        self.last_date_time_conf.save()

        # set session
        new_date_time = f"{new_date} {new_time}"
        dt_format = '%Y-%m-%d %H:%M'
        new_utc_date_time = datetime.strptime(new_date_time, dt_format)
        self.page.session.set('utc_date_time', new_utc_date_time)

        Toast.show_success(e.page)
        self.__refresh_language()
        self.__change_theme()
        self.update()

    def __change_theme(self):
        if self.last_preference.theme == '1':
            self.page.theme_mode = ft.ThemeMode.LIGHT
        elif self.last_preference.theme == '2':
            self.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.page.theme_mode = ft.ThemeMode.SYSTEM
            

    def __refresh_language(self):
        lang = Preference.get().language
        language_items = Language.select()
        for item in language_items:
            self.page.session.set(
                item.code, item.english if lang == 0 else item.chinese)

    def __reset_data(self, e):
        self.last_preference = Preference.get()
        self.last_limitations = Limitations.get()
        self.last_date_time_conf = DateTimeConf.get()

        self.system_unit.value = self.last_preference.system_unit
        self.language.value = self.last_preference.language
        self.data_refresh_interval.value = self.last_preference.data_refresh_interval
        self.preference_card.update()

        self.__update_limitations()

        self.utc_date.value = self.last_date_time_conf.utc_date
        self.utc_time.value = self.last_date_time_conf.utc_time.strftime(
            '%H:%M')
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
            self.page.session.get("lang.button.save"),
            width=120, height=40,
            on_click=self.__save_data
        )
        self.reset_button = ft.OutlinedButton(
            self.page.session.get("lang.button.reset"),
            width=120, height=40,
            on_click=self.__reset_data
        )

        self.content = ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE,
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
                                self.reset_button
                            ])
                    ]
                )
            ]
        )

    def did_mount(self):
        self.__update_limitations()
        self._task = self.page.run_task(self.__refresh_utc_date_time)

    async def __refresh_utc_date_time(self):
        while True:
            utc_date_time = self.page.session.get("utc_date_time")
            self.utc_date_time.value = utc_date_time.strftime('%Y-%m-%d %H:%M')
            self.utc_date_time.update()
            await asyncio.sleep(1)

    def will_unmount(self):
        if self._task:
            self._task.cancel()