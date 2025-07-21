import logging
import flet as ft

from db.models.event_log import EventLog


class EventNote(ft.AlertDialog):
    def __init__(self, id):
        super().__init__()
        self.id = id

    def build(self):
        try:
            self.title = ft.Text(self.page.session.get("lang.common.note"))
            event_log: EventLog = EventLog.get_by_id(self.id)
            if event_log is not None:
                self.content = ft.Text(value=event_log.note)
        except:
            logging.exception('exception occured at EventNote.build')
