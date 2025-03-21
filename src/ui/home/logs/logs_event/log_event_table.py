from typing import override

from db.models.event_log import EventLog
from ui.common.abstract_table import AbstractTable


class LogEventTable(AbstractTable):
    @override
    def load_total(self):
        return EventLog.select().count()

    @override
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

    @override
    def create_columns(self):
        return [
            "No.",
            "Breach Reason",
            "Started At",
            "Started Position",
            "Ended At",
            "Ended Position",
            "Note"
        ]
