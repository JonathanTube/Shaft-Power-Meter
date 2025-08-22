import asyncio
from datetime import datetime
import logging
import flet as ft
from common.global_data import gdata
from db.models.data_log import DataLog
from ui.common.custom_card import CustomCard
from db.models.date_time_conf import DateTimeConf


class GeneralDateTime(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def build(self):
        try:
            if self.page and self.page.session:
                s = self.page.session
                utc = gdata.configDateTime.utc
                fmt = gdata.configDateTime.date_format
                self.utc_date = ft.TextField(
                    label=s.get("lang.setting.date"),
                    col={"md": 6},
                    can_request_focus=False,
                    value=utc.strftime(fmt) if utc else '',
                    on_click=lambda e: e.page.open(
                        ft.DatePicker(
                            on_change=self.__handle_date_change,
                            current_date=utc.date() if utc else datetime.now()
                        )
                    )
                )

                self.utc_time = ft.TextField(
                    label=s.get("lang.setting.time"),
                    col={"md": 6},
                    can_request_focus=False,
                    value=utc.strftime('%H:%M') if utc else '',
                    on_click=lambda e: e.page.open(
                        ft.TimePicker(
                            on_change=self.__handle_time_change
                        )
                    )
                )

                self.date_format = ft.Dropdown(
                    label=s.get("lang.setting.date_format"), col={"md": 6},
                    value=fmt,
                    options=[
                        ft.DropdownOption(text="YYYY-MM-DD", key="%Y-%m-%d"),
                        ft.DropdownOption(text="DD-MM-YYYY", key="%d-%m-%Y"),
                        ft.DropdownOption(text="MM-DD-YYYY", key="%m-%d-%Y")
                    ]
                )

                self.sync_with_gps = ft.Checkbox(
                    label=s.get("lang.setting.sync_with_gps"),
                    col={"md": 6},
                    visible=gdata.configCommon.enable_gps,
                    value=gdata.configDateTime.sync_with_gps
                )

                self.custom_card = CustomCard(
                    s.get("lang.setting.utc_date_time_conf"),
                    ft.ResponsiveRow(
                        controls=[
                            self.utc_date,
                            self.utc_time,
                            self.date_format,
                            self.sync_with_gps
                        ]
                    ),
                    col={"xs": 12}
                )
                self.content = self.custom_card
        except:
            logging.exception('exception occured at GeneralDateTime.build')

    def reset(self):
        try:
            if self.page and self.page.session:
                s = self.page.session
                if self.utc_date:
                    self.utc_date.label = s.get("lang.setting.date")
                    utc = gdata.configDateTime.utc
                    fmt = gdata.configDateTime.date_format
                    self.utc_date.value = utc.strftime(fmt)

                if self.utc_time:
                    self.utc_time.label = s.get("lang.setting.time")

                if self.date_format:
                    self.date_format.label = s.get("lang.setting.date_format")

                if self.sync_with_gps:
                    self.sync_with_gps.label = s.get("lang.setting.sync_with_gps")

                if self.custom_card:
                    self.custom_card.set_title(s.get("lang.setting.utc_date_time_conf"))
        except:
            logging.exception('exception occured at GeneralDateTime.before_update')

    def __handle_date_change(self, e):
        try:
            if e.control and e.control.value:
                utc_date = e.control.value.strftime('%Y-%m-%d')
                if self.utc_date and self.utc_date.page:
                    self.utc_date.value = utc_date
                    self.utc_date.update()
        except:
            logging.exception('exception occured at GeneralDateTime.__handle_date_change')

    def __handle_time_change(self, e):
        try:
            if e.control and e.control.value:
                utc_time = e.control.value.strftime('%H:%M')
                if self.utc_time and self.utc_time.page:
                    self.utc_time.value = utc_time
                    self.utc_time.update()
        except:
            logging.exception('exception occured at GeneralDateTime.__handle_time_change')

    def save_data(self, user_id: int):
        """异步保存，避免阻塞 UI"""
        standard_date_time_format = f'{gdata.configDateTime.date_format} %H:%M:%S'
        new_date = self.utc_date.value
        new_time = self.utc_time.value

        try:
            # 更新时间配置
            new_utc = datetime.strptime(f"{new_date} {new_time}:00", standard_date_time_format)
            DateTimeConf.update(
                utc_date_time=new_utc, system_date_time=datetime.now(),
                date_format=self.date_format.value, sync_with_gps=self.sync_with_gps.value
            ).execute()
            # 刷新时间相关配置
            gdata.configDateTime.set_default_value()
        except:
            logging.exception("exception occured at GeneralDateTime.save_data_async")
