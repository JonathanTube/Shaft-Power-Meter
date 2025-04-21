import asyncio
import flet as ft
from typing import Callable

from db.models.alarm_log import AlarmLog


class AlarmButton(ft.TextButton):

    def __init__(self, on_click: Callable):
        super().__init__()
        self.task = None
        self.blinking = False

        self.icon = ft.Icons.WARNING_OUTLINED
        self.icon_color = ft.Colors.INVERSE_SURFACE
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(0)),
            color=ft.Colors.INVERSE_SURFACE
        )
        self.on_click = on_click

        self.badge = None

    def build(self):
        self.text = self.page.session.get("lang.home.tab.alarm")

    def update_badge(self):
        count = AlarmLog.select().where(AlarmLog.acknowledge_time == None).count()
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

    async def __blink(self):
        while self.blinking:
            if self.style.bgcolor == ft.Colors.INVERSE_SURFACE:
                self.style.bgcolor = ft.Colors.RED
            else:
                self.style.bgcolor = ft.Colors.INVERSE_SURFACE
            self.update()
            await asyncio.sleep(1)

    def start_blink(self):
        self.blinking = True
        self.task = self.page.create_task(self.__blink())

    def stop_blink(self):
        self.blinking = False
        if self.task is not None:
            self.task.cancel()
            self.task = None

    def will_unmount(self):
        self.stop_blink()
