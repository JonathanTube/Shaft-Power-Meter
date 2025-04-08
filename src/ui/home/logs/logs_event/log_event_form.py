import flet as ft

from db.models.breach_reason import BreachReason
from db.models.event_log import EventLog
from typing import Callable


class LogEventForm(ft.AlertDialog):
    def __init__(self, event_id: int, callback: Callable):
        super().__init__()
        self.event_id = event_id
        self.callback = callback
        self.title = ft.Text("Event Log")
        self.__load_data()

    def __load_data(self):
        self.breach_reasons = BreachReason.select()
        self.event_log = EventLog.select().where(EventLog.id == self.event_id).first()

    def build(self):
        started_at = ft.TextField(
            label="Date/Time of Power Reaserve Breach",
            value=self.event_log.started_at,
            read_only=True,
            disabled=True
        )

        start_position = ft.TextField(
            label="Ship position of Power Reserve Breach",
            value=self.event_log.started_position,
            read_only=True,
            disabled=True
        )

        ended_at = ft.TextField(
            label="Date/Time when returning to limited power",
            value=self.event_log.started_at,
            read_only=True,
            disabled=True
        )

        ended_position = ft.TextField(
            label="Ship position when returning to limited power",
            value=self.event_log.ended_position,
            read_only=True,
            disabled=True
        )

        reason = ft.Dropdown(
            label="Reason for Power Reserve Breach",
            options=[ft.dropdown.Option(key=reason.id, text=reason.reason)
                     for reason in self.breach_reasons],
            value=self.event_log.breach_reason,
            on_change=lambda e: setattr(
                self.event_log, "breach_reason", e.control.value)
        )

        note = ft.TextField(
            label="Note",
            multiline=True,
            on_change=lambda e: setattr(
                self.event_log, "note", e.control.value)
        )

        beaufort_number = ft.TextField(
            label="Beaufort number",
            value=self.event_log.beaufort_number,
            on_change=lambda e: setattr(
                self.event_log, "beaufort_number", e.control.value)
        )

        wave_height = ft.TextField(
            label="Wave height",
            value=self.event_log.wave_height,
            on_change=lambda e: setattr(
                self.event_log, "wave_height", e.control.value)
        )

        ice_condition = ft.TextField(
            label="Ice condition",
            value=self.event_log.ice_condition,
            on_change=lambda e: setattr(
                self.event_log, "ice_condition", e.control.value)
        )

        self.content = ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE,
            controls=[
                started_at,
                start_position,
                ended_at,
                ended_position,
                reason,
                note,
                beaufort_number,
                wave_height,
                ice_condition
            ]
        )

        self.actions = [
            ft.ElevatedButton(
                text="Save",
                on_click=self.__save
            ),
            ft.TextButton(
                text="Cancel",
                on_click=self.__on_close
            )
        ]

    def __on_close(self, e):
        e.page.close(self)

    def __save(self, e):
        self.event_log.save()
        e.page.close(self)
        self.callback()
