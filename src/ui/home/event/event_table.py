import flet as ft

from db.models.event_log import EventLog
from ui.common.abstract_table import AbstractTable
from ui.home.event.event_form import EventForm


class EventTable(AbstractTable):
    def load_total(self):
        start_date = self.kwargs.get('start_date')
        end_date = self.kwargs.get('end_date')
        sql = EventLog.select()
        if start_date and end_date:
            sql = sql.where(EventLog.started_at >= start_date,
                            EventLog.started_at <= end_date)

        return sql.count()

    def load_data(self):
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
            EventLog.note
        )
        if start_date and end_date:
            sql = sql.where(EventLog.started_at >= start_date,
                            EventLog.started_at <= end_date)

        data = sql.order_by(EventLog.id.desc()).paginate(
            self.current_page, self.page_size)

        return [[
                item.id,
                item.breach_reason.reason if item.breach_reason else "",
                item.started_at,
                item.started_position,
                item.ended_at,
                item.ended_position,
                item.acknowledged_at,
                item.note
                ] for item in data]

    def get_columns(self):
        session = self.page.session
        return [
            session.get("lang.common.no"),
            session.get("lang.common.breach_reason"),
            session.get("lang.common.start_date"),
            session.get("lang.common.start_position"),
            session.get("lang.common.end_date"),
            session.get("lang.common.end_position"),
            session.get("lang.common.acknowledged_at"),
            session.get("lang.common.note")
        ]

    def create_columns(self):
        return self.get_columns()

    def has_operations(self):
        return True

    def create_operations(self, items: list):
        show_reason = items[1] is None or items[1].strip() == ""
        show_note = items[7] is not None and items[7].strip() != ""
        return ft.Row(controls=[
            ft.IconButton(
                icon=ft.icons.WARNING,
                icon_color=ft.colors.RED,
                icon_size=20,
                visible=show_reason,
                on_click=lambda e: self.page.open(
                    EventForm(items[0], self.__update_table)
                )
            ),
            ft.IconButton(
                icon=ft.icons.NOTE,
                icon_color=ft.colors.GREEN,
                icon_size=20,
                visible=show_note
            )
        ])

    def __update_table(self):
        self.search(**self.kwargs)

    def before_update(self):
        self.update_columns(self.get_columns())
