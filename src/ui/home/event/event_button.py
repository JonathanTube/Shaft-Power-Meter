import asyncio
import logging
import flet as ft
from typing import Callable
from common.global_data import gdata


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
            self.visible = gdata.configCommon.shapoli
            if not self.visible:
                return

            self.text = self.page.session.get("lang.home.tab.event")
        except:
            logging.exception('exception occured at EventButton.build')

    async def loop(self):
        while self.task_running:
            try:
                if self.page:
                    count = gdata.configEvent.not_confirmed_count
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
        if not gdata.configCommon.shapoli:
            return
        self.task = self.page.run_task(self.loop)

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()
