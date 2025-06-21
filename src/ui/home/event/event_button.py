import asyncio
import logging
import flet as ft
from typing import Callable

from db.models.event_log import EventLog
from db.models.system_settings import SystemSettings


class EventButton(ft.TextButton):
    def __init__(self, style: ft.ButtonStyle, on_click: Callable):
        super().__init__()

        self.style = style

        self.task = None
        self.task_running = True

        self.icon = ft.Icons.EVENT_OUTLINED
        self.icon_color = ft.Colors.INVERSE_SURFACE
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(0)),
            color=ft.Colors.INVERSE_SURFACE
        )
        self.on_click = on_click

    def build(self):
        system_settings: SystemSettings = SystemSettings.get()
        self.text = self.page.session.get("lang.home.tab.event")
        self.visible = system_settings.sha_po_li

    async def __loop(self):
        while self.task_running:
            try:
                count = EventLog.select().where(EventLog.breach_reason == None).count()
                if count > 0:
                    self.badge = ft.Badge(text=str(count), bgcolor=ft.Colors.RED, text_color=ft.Colors.WHITE, label_visible=True)
                else:
                    self.badge = None
                self.update()
            except:
                logging.exception("exception occured at EventButton.__loop")
                self.task_running = False
                break
            finally:
                await asyncio.sleep(5)

    def did_mount(self):
        self.task = self.page.run_task(self.__loop)

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()
