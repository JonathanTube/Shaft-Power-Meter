import asyncio
import logging
import flet as ft
from typing import Callable

from db.models.event_log import EventLog
from peewee import fn


class EventButton(ft.TextButton):
    def __init__(self, style: ft.ButtonStyle, on_click: Callable):
        super().__init__()

        self.task = None
        self.task_running = True

        self.style = style

        self.icon = ft.Icons.EVENT_OUTLINED
        self.icon_color = ft.Colors.INVERSE_SURFACE

        self.on_click = on_click

    def build(self):
        try:
            self.text = self.page.session.get("lang.home.tab.event")
        except:
            logging.exception('exception occured at EventButton.build')

    async def __loop(self):
        while self.task_running:
            try:
                if self.page:
                    count = (EventLog.select(fn.COUNT(EventLog.id)).where(EventLog.breach_reason.is_null(True)).scalar() or 0)
                    if count > 0:
                        self.badge = ft.Badge(text=str(count), bgcolor=ft.Colors.RED, text_color=ft.Colors.WHITE, label_visible=True)
                    else:
                        self.badge = None
                    self.update()
            except:
                logging.exception("exception occured at EventButton.__loop")
                self.task_running = False
                break
            await asyncio.sleep(5)

    def did_mount(self):
        self.task = self.page.run_task(self.__loop)

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()
