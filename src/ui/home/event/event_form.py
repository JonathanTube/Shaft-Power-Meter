import logging
import flet as ft
from common.operation_type import OperationType
from db.models.breach_reason import BreachReason
from db.models.event_log import EventLog
from typing import Callable

from db.models.operation_log import OperationLog
from db.models.user import User
from ui.common.permission_check import PermissionCheck
from common.global_data import gdata
from playhouse.shortcuts import model_to_dict

from ui.common.toast import Toast


class EventForm(ft.AlertDialog):
    def __init__(self, event_id: int, callback: Callable):
        super().__init__()
        self.event_id = event_id
        self.callback = callback
        self.barrier_color = ft.Colors.TRANSPARENT
        self.__load_data()

    def __load_data(self):
        try:
            self.breach_reasons = BreachReason.select()
            self.event_log: EventLog = EventLog.select().where(EventLog.id == self.event_id).first()
        except:
            logging.exception('exception occured at EventForm.__load_data')


    def build(self):
        try:
            self.title = ft.Text(self.page.session.get("lang.log.event_log"))
        
            self.breach_reason = ft.Dropdown(
                expand=True,
                width=500,
                label=self.page.session.get("lang.event.reason_for_power_reserve_breach"),
                options=[ft.dropdown.Option(key=reason.id, text=reason.reason) for reason in self.breach_reasons],
                value=self.event_log.breach_reason
            )

            self.note = ft.TextField(
                label=self.page.session.get("lang.event.note"),
                multiline=True,
                value=self.event_log.note
            )

            self.beaufort_number = ft.TextField(
                label=self.page.session.get("lang.event.beaufort_number"),
                value=self.event_log.beaufort_number
            )

            self.wave_height = ft.TextField(
                label=self.page.session.get("lang.event.wave_height"),
                value=self.event_log.wave_height
            )

            self.ice_condition = ft.TextField(
                label=self.page.session.get("lang.event.ice_condition"),
                value=self.event_log.ice_condition
            )

            cols = ft.Column(
                controls=[
                    self.breach_reason,
                    self.note,
                    self.beaufort_number,
                    self.wave_height,
                    self.ice_condition
                ]
            )

            self.content = ft.Column(
                scroll=ft.ScrollMode.ADAPTIVE,
                height=400,
                controls=[
                    ft.Container(
                        width=500,
                        padding=30,
                        content=cols
                    )
                ])

            self.actions = [
                ft.ElevatedButton(text=self.page.session.get("lang.button.save"), on_click=self.__on_click_save),
                ft.TextButton(text=self.page.session.get("lang.button.cancel"), on_click=self.__on_close)
            ]
        except:
            logging.exception('exception occured at EventForm.build')


    def __on_close(self, e):
        e.page.close(self)

    def __on_click_save(self, e):
        self.event_log.breach_reason = self.breach_reason.value
        self.event_log.note = self.note.value
        self.event_log.beaufort_number = self.beaufort_number.value
        self.event_log.wave_height = self.wave_height.value
        self.event_log.ice_condition = self.ice_condition.value
        if self.event_log.breach_reason is None or self.event_log.beaufort_number is None or self.event_log.beaufort_number == "" or self.event_log.wave_height is None or self.event_log.wave_height == "" or self.event_log.ice_condition is None or self.event_log.ice_condition == "":
            Toast.show_warning(self.page, self.page.session.get("lang.event.please_input_all_fields_except_note"))
            return
        self.page.open(PermissionCheck(self.__save_data, 1))

    def __save_data(self, user: User):
        try:
            self.event_log.save()
            OperationLog.create(
                user_id=user.id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.IO_CONF,
                operation_content=model_to_dict(self.event_log)
            )
            self.page.close(self)
            self.callback()
        except:
            Toast.show_error(self.page)
