import flet as ft
from typing import Callable

from db.models.event_log import EventLog


class EventButton(ft.TextButton):
    def __init__(self, on_click: Callable):
        super().__init__()

        self.icon = ft.Icons.EVENT_OUTLINED
        self.icon_color = ft.Colors.INVERSE_SURFACE
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(0)),
            color=ft.Colors.INVERSE_SURFACE
        )
        self.on_click = on_click

    def build(self):
        self.text = self.page.session.get("lang.home.tab.event")

    def update_badge(self):
        count = EventLog.select().where(EventLog.breach_reason == None).count()
        if count > 0:
            self.badge = ft.Badge(
                text=str(count),
                bgcolor=ft.Colors.RED,
                text_color=ft.Colors.WHITE,
                label_visible=True
            )
        else:
            self.badge = None
        self.update()
