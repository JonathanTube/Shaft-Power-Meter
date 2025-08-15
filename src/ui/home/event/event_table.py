import logging
import flet as ft

from db.models.event_log import EventLog
from ui.common.abstract_table import AbstractTable
from ui.home.event.event_form import EventForm
from ui.home.event.event_note import EventNote
from common.global_data import gdata
from peewee import fn


class EventTable(AbstractTable):
    def __init__(self):
        super().__init__()

    def load_total(self):
        try:
            start_date = self.kwargs.get('start_date')
            end_date = self.kwargs.get('end_date')

            query = EventLog.select(fn.COUNT(EventLog.id))

            if start_date and end_date:
                query = query.where(
                    (EventLog.started_at >= start_date) &
                    (EventLog.started_at <= end_date)
                )

            return query.scalar() or 0
        except:
            logging.exception('exception occurred at EventTable.load_total')
            return 0

    def load_data(self):
        try:
            start_date = self.kwargs.get('start_date')
            end_date = self.kwargs.get('end_date')
            sql = EventLog.select(
                EventLog.id,
                EventLog.breach_reason,
                EventLog.started_at,
                EventLog.started_position,
                EventLog.ended_at,
                EventLog.ended_position,
                EventLog.acknowledged_at,
                EventLog.beaufort_number,
                EventLog.wave_height,
                EventLog.ice_condition,
                EventLog.note
            )
            if start_date and end_date:
                sql = sql.where(EventLog.started_at >= start_date, EventLog.started_at <= end_date)

            data = sql.order_by(EventLog.id.desc()).paginate(self.current_page, self.page_size)

            date_time_format = f"{gdata.configDateTime.date_format} %H:%M:%S"
            return [[
                    item.id,
                    item.breach_reason.reason if item.breach_reason else "",
                    item.started_at.strftime(date_time_format) if item.started_at else "",
                    item.started_position,
                    item.ended_at.strftime(date_time_format) if item.ended_at else "",
                    item.ended_position,
                    item.beaufort_number,
                    item.wave_height,
                    item.ice_condition,
                    item.acknowledged_at.strftime(date_time_format) if item.acknowledged_at else ""
                    ] for item in data]
        except:
            logging.exception('exception occured at EventTable.load_data')

    def get_columns(self):
        try:
            session = self.page.session
            return [
                session.get("lang.common.no"),
                session.get("lang.common.breach_reason"),
                session.get("lang.common.start_date"),
                session.get("lang.common.start_position"),
                session.get("lang.common.end_date"),
                session.get("lang.common.end_position"),
                session.get("lang.event.beaufort_number"),
                session.get("lang.event.wave_height"),
                session.get("lang.event.ice_condition"),
                session.get("lang.common.acknowledged_at")
            ]
        except:
            logging.exception('exception occured at EventTable.get_columns')

    def create_columns(self):
        return self.get_columns()

    def has_operations(self):
        return True

    def create_operations(self, items: list):
        try:
            show_reason = items[1] is None or items[1].strip() == ""
            show_note = items[7] is not None and items[7].strip() != ""
            return ft.Row(controls=[
                ft.IconButton(
                    icon=ft.Icons.WARNING,
                    icon_color=ft.Colors.RED,
                    icon_size=20,
                    visible=show_reason,
                    on_click=lambda e: self.page.open(EventForm(items[0], self.__update_table))
                ),
                ft.IconButton(
                    icon=ft.Icons.NOTE,
                    icon_color=ft.Colors.GREEN,
                    icon_size=20,
                    visible=show_note,
                    on_click=lambda e: self.page.open(EventNote(items[0]))
                )
            ])
        except:
            logging.exception('exception occured at EventTable.create_operations')

        return None

    def __update_table(self):
        self.search(**self.kwargs)
