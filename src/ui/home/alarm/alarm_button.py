import asyncio
import flet as ft
from typing import Callable

from db.models.alarm_log import AlarmLog


class AlarmButton(ft.TextButton):
    def __init__(self, on_click: Callable):
        super().__init__()
        self.task = None
        self.blinking = False
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(10)),
            color=ft.Colors.INVERSE_SURFACE
        )
        self.icon = ft.Icons.WARNING_OUTLINED
        self.icon_color = ft.Colors.INVERSE_SURFACE
        self.on_click = on_click

        self.badge = None

    def build(self):
        self.text = self.page.session.get("lang.home.tab.alarm")

    def update_alarm(self):
        count = AlarmLog.select().where(AlarmLog.acknowledge_time.is_null()).count()
        if count > 0:
            self.badge = ft.Badge(text=str(count), bgcolor=ft.Colors.RED, text_color=ft.Colors.WHITE, label_visible=True)
            self.start_blink()
        else:
            self.badge = None
            self.stop_blink()
        self.update()

    async def __blink(self):
        cnt = 0
        while self.blinking:
            if cnt % 2 == 0:
                self.style = ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(10)),
                    color=ft.Colors.WHITE,
                    bgcolor=ft.Colors.RED
                )
                self.icon_color = ft.Colors.WHITE
            else:
                self.style = ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(10)),
                    color=ft.Colors.INVERSE_SURFACE,
                    bgcolor=ft.Colors.SURFACE
                )
                self.icon_color = ft.Colors.INVERSE_SURFACE
            self.update()
            await asyncio.sleep(1)
            cnt += 1

    def start_blink(self):
        if not self.blinking:
            self.blinking = True
            self.task = self.page.run_task(self.__blink)

    def stop_blink(self):
        self.blinking = False
        if self.task is not None:
            self.task.cancel()
            self.task = None

    def will_unmount(self):
        self.stop_blink()
