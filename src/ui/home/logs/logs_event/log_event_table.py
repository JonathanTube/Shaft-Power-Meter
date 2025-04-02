from db.models.event_log import EventLog
from ui.common.abstract_table import AbstractTable


class LogEventTable(AbstractTable):
    def load_total(self):
        return EventLog.select().count()

    def load_data(self):
        data = EventLog.select(
            EventLog.id,
            EventLog.breach_reason,
            EventLog.started_at,
            EventLog.started_position,
            EventLog.ended_at,
            EventLog.ended_position,
            EventLog.note
        ).order_by(EventLog.id.desc()).paginate(self.current_page, self.page_size)

        return [[
                item.id,
                item.breach_reason.reason,
                item.started_at,
                item.started_position,
                item.ended_at,
                item.ended_position,
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
            session.get("lang.common.note")
        ]

    def create_columns(self):
        return self.get_columns()

    def before_update(self):
        self.update_columns(self.get_columns())
