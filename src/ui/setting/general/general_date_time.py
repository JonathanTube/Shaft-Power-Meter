from datetime import datetime
import flet as ft
import asyncio
from common.global_data import gdata
from ui.common.custom_card import CustomCard
from db.models.date_time_conf import DateTimeConf
from db.models.operation_log import OperationLog
from common.operation_type import OperationType
from playhouse.shortcuts import model_to_dict


class GeneralDateTime(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self._task = None
        self.date_time_conf: DateTimeConf = DateTimeConf.get()

    def build(self):
        s = self.page.session
        utc_date_time = gdata.utc_date_time
        self.utc_date_time = ft.TextField(
            label=s.get("lang.setting.current_utc_date_time"),
            col={"md": 12},
            read_only=True,
            can_request_focus=False,
            value=utc_date_time
        )

        self.utc_date = ft.TextField(
            label=s.get("lang.setting.date"),
            col={"md": 6},
            can_request_focus=False,
            value=self.date_time_conf.utc_date_time.strftime('%Y-%m-%d'),
            on_click=lambda e: e.page.open(
                ft.DatePicker(
                    on_change=self.__handle_date_change,
                    current_date=self.date_time_conf.utc_date_time.date()
                )
            )
        )

        self.utc_time = ft.TextField(
            label=s.get("lang.setting.time"),
            col={"md": 6},
            can_request_focus=False,
            value=self.date_time_conf.utc_date_time.strftime('%H:%M'),
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

        self.sync_with_gps = ft.Checkbox(label=s.get("lang.setting.sync_with_gps"), col={"md": 6}, value=self.date_time_conf.sync_with_gps)

        self.content = CustomCard(
            s.get("lang.setting.utc_date_time_conf"),
            ft.ResponsiveRow(
                controls=[
                    self.utc_date_time,
                    self.utc_date,
                    self.utc_time,
                    self.date_format,
                    self.sync_with_gps
                ]
            ),
            col={"xs": 12}
        )

    def __handle_date_change(self, e):
        utc_date = e.control.value.strftime('%Y-%m-%d')
        self.utc_date.value = utc_date
        self.utc_date.update()

    def __handle_time_change(self, e):
        utc_time = e.control.value.strftime('%H:%M')
        self.utc_time.value = utc_time
        self.utc_time.update()

    async def __refresh_utc_date_time(self):
        while True:
            if self.utc_date_time:
                utc_date_time = gdata.utc_date_time
                self.utc_date_time.value = utc_date_time.strftime(f'{self.date_time_conf.date_format} %H:%M')
                self.utc_date_time.update()
            await asyncio.sleep(1)

    def did_mount(self):
        self._task = self.page.run_task(self.__refresh_utc_date_time)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    def save_data(self, user_id: int):
        standard_date_time_format = '%Y-%m-%d %H:%M:%S'
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
