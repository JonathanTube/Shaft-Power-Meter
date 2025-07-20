from datetime import datetime
import logging
import flet as ft
from common.global_data import gdata
from db.models.data_log import DataLog
from db.models.system_settings import SystemSettings
from ui.common.custom_card import CustomCard
from db.models.date_time_conf import DateTimeConf
from db.models.operation_log import OperationLog
from common.operation_type import OperationType
from playhouse.shortcuts import model_to_dict


class GeneralDateTime(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.date_time_conf: DateTimeConf = DateTimeConf.get()
        self.system_settings: SystemSettings = SystemSettings.get()

    def build(self):
        try:
            if self.page and self.page.session:
                s = self.page.session

                utc_date_time = self.date_time_conf.utc_date_time

                self.utc_date = ft.TextField(
                    label=s.get("lang.setting.date"),
                    col={"md": 6},
                    can_request_focus=False,
                    value=utc_date_time.strftime(self.date_time_conf.date_format) if utc_date_time is not None else '',
                    on_click=lambda e: e.page.open(
                        ft.DatePicker(
                            on_change=self.__handle_date_change,
                            current_date=utc_date_time.date() if utc_date_time is not None else datetime.now()
                        )
                    )
                )

                self.utc_time = ft.TextField(
                    label=s.get("lang.setting.time"),
                    col={"md": 6},
                    can_request_focus=False,
                    value=utc_date_time.strftime('%H:%M') if utc_date_time is not None else '',
                    on_click=lambda e: e.page.open(
                        ft.TimePicker(
                            on_change=self.__handle_time_change
                        )
                    )
                )

                self.date_format = ft.Dropdown(
                    label=s.get("lang.setting.date_format"), col={"md": 6},
                    value=self.date_time_conf.date_format,
                    options=[ft.DropdownOption(text="YYYY-MM-dd", key="%Y-%m-%d"),
                             ft.DropdownOption(text="YYYY/MM/dd", key="%Y/%m/%d"),
                             ft.DropdownOption(text="dd/MM/YYYY", key="%d/%m/%Y"),
                             ft.DropdownOption(text="MM/dd/YYYY", key="%m/%d/%Y")]
                )

                self.sync_with_gps = ft.Checkbox(
                    label=s.get("lang.setting.sync_with_gps"),
                    col={"md": 6},
                    visible=self.system_settings.enable_gps,
                    value=self.date_time_conf.sync_with_gps
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

    def before_update(self):
        try:
            if self.page and self.page.session:
                s = self.page.session
                if self.utc_date is not None:
                    self.utc_date.label = s.get("lang.setting.date")
                    if self.date_time_conf and self.date_time_conf.utc_date_time:
                        self.utc_date.value = self.date_time_conf.utc_date_time.strftime(self.date_time_conf.date_format)

                if self.utc_time is not None:
                    self.utc_time.label = s.get("lang.setting.time")

                if self.date_format is not None:
                    self.date_format.label = s.get("lang.setting.date_format")

                if self.sync_with_gps is not None:
                    self.sync_with_gps.label = s.get("lang.setting.sync_with_gps")

                if self.custom_card is not None:
                    self.custom_card.set_title(s.get("lang.setting.utc_date_time_conf"))
        except:
            logging.exception('exception occured at GeneralDateTime.build')

    def __handle_date_change(self, e):
        try:
            if e.control is not None and e.control.value is not None:
                utc_date = e.control.value.strftime('%Y-%m-%d')
                if self.utc_date and self.utc_date.page:
                    self.utc_date.value = utc_date
                    self.utc_date.update()
        except:
            logging.exception('exception occured at GeneralDateTime.__handle_date_change')

    def __handle_time_change(self, e):
        try:
            if e.control is not None and e.control.value is not None:
                utc_time = e.control.value.strftime('%H:%M')
                if self.utc_time and self.utc_time.page:
                    self.utc_time.value = utc_time
                    self.utc_time.update()
        except:
            logging.exception('exception occured at GeneralDateTime.__handle_time_change')

    def save_data(self, user_id: int):
        if self.page is None:
            return

        if self.date_time_conf is None:
            return

        standard_date_time_format = f'{self.date_time_conf.date_format} %H:%M:%S'
        # save date time conf
        new_date = self.utc_date.value
        new_time = self.utc_time.value
        self.date_time_conf.utc_date_time = datetime.strptime(f"{new_date} {new_time}:00", standard_date_time_format)

        self.date_time_conf.system_date_time = datetime.now()
        self.date_time_conf.date_format = self.date_format.value
        self.date_time_conf.sync_with_gps = self.sync_with_gps.value
        gdata.enable_utc_time_sync_with_gps = self.sync_with_gps.value
        self.date_time_conf.save()
        OperationLog.create(
            user_id=user_id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.GENERAL_UTC_DATE_TIME,
            operation_content=model_to_dict(self.date_time_conf)
        )

        new_date_time = f"{new_date} {new_time}:00"

        new_utc_date_time = datetime.strptime(new_date_time, standard_date_time_format)
        gdata.utc_date_time = new_utc_date_time

        # 需要删除掉之前大于当前时间的数据，否则会影响eexi breach判断
        DataLog.delete().where(DataLog.utc_date_time >= gdata.utc_date_time).execute()

        self.page.update()
