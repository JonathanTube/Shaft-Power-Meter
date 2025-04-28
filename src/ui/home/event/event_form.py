import flet as ft
import subprocess
from common.operation_type import OperationType
from db.models.breach_reason import BreachReason
from db.models.event_log import EventLog
from typing import Callable

from db.models.opearation_log import OperationLog
from db.models.user import User
from ui.common.permission_check import PermissionCheck
from common.global_data import gdata
from playhouse.shortcuts import model_to_dict


class EventForm(ft.AlertDialog):
    def __init__(self, event_id: int, callback: Callable):
        super().__init__()
        self.event_id = event_id
        self.callback = callback
        self.title = ft.Text("Event Log")
        self.__load_data()

    def __load_data(self):
        self.breach_reasons = BreachReason.select()
        self.event_log: EventLog = EventLog.select().where(EventLog.id == self.event_id).first()

    def build(self):
        started_at = ft.TextField(
            label=self.page.session.get("lang.event.date_time_of_power_reserve_breach"),
            value=self.event_log.started_at,
            read_only=True,
            disabled=True
        )

        start_position = ft.TextField(
            label=self.page.session.get("lang.event.ship_position_of_power_reserve_breach"),
            value=self.event_log.started_position,
            read_only=True,
            disabled=True
        )

        ended_at = ft.TextField(
            label=self.page.session.get("lang.event.date_time_when_returning_to_limited_power"),
            value=self.event_log.started_at,
            read_only=True,
            disabled=True
        )

        ended_position = ft.TextField(
            label=self.page.session.get("lang.event.ship_position_when_returning_to_limited_power"),
            value=self.event_log.ended_position,
            read_only=True,
            disabled=True
        )

        self.breach_reason = ft.Dropdown(
            label=self.page.session.get("lang.event.reason_for_power_reserve_breach"),
            options=[ft.dropdown.Option(key=reason.id, text=reason.reason) for reason in self.breach_reasons],
            value=self.event_log.breach_reason
        )

        self.note = ft.TextField(
            label=self.page.session.get("lang.event.note"),
            multiline=True,
            value=self.event_log.note,
            on_click=lambda e: subprocess.run(["osk.exe"])
        )

        self.beaufort_number = ft.TextField(
            label=self.page.session.get("lang.event.beaufort_number"),
            value=self.event_log.beaufort_number,
            on_click=lambda e: subprocess.run(["osk.exe"])
        )

        self.wave_height = ft.TextField(
            label=self.page.session.get("lang.event.wave_height"),
            value=self.event_log.wave_height,
            on_click=lambda e: subprocess.run(["osk.exe"])
        )

        self.ice_condition = ft.TextField(
            label=self.page.session.get("lang.event.ice_condition"),
            value=self.event_log.ice_condition,
            on_click=lambda e: subprocess.run(["osk.exe"])
        )

        self.content = ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE,
            controls=[
                started_at,
                start_position,
                ended_at,
                ended_position,
                self.breach_reason,
                self.note,
                self.beaufort_number,
                self.wave_height,
                self.ice_condition
            ]
        )

        self.actions = [
            ft.ElevatedButton(text=self.page.session.get("lang.button.save"), on_click=self.__on_click_save),
            ft.TextButton(text=self.page.session.get("lang.button.cancel"), on_click=self.__on_close)
        ]

    def __on_close(self, e):
        e.page.close(self)

    def __on_click_save(self, e):
        self.page.open(PermissionCheck(self.__save_data, 1))

    def __save_data(self, user: User):
        self.event_log.breach_reason = self.breach_reason.value
        self.event_log.note = self.note.value
        self.event_log.beaufort_number = self.beaufort_number.value
        self.event_log.wave_height = self.wave_height.value
        self.event_log.ice_condition = self.ice_condition.value
        self.event_log.save()
        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.IO_CONF,
            operation_content=model_to_dict(self.event_log)
        )
        self.page.close(self)
        self.callback()
