import logging
import flet as ft


class EventNote(ft.AlertDialog):
    def __init__(self, content: str):
        super().__init__()
        self.content = content

    def build(self):
        try:
            self.title = ft.Text(self.page.session.get("lang.common.note"))
            self.content = ft.Text(value=self.content)
        except:
            logging.exception('exception occured at EventNote.build')

