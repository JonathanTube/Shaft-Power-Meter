import asyncio
import logging
import flet as ft
from typing import Callable

from db.models.alarm_log import AlarmLog


class AlarmButton(ft.TextButton):
    def __init__(self, style: ft.ButtonStyle, on_click: Callable):
        super().__init__()
        self.style = style
        self.icon = ft.Icons.WARNING_ROUNDED
        self.on_click = on_click

        self.task = None
        self.task_running = True

        self.alarm_count = 0
        self.not_ack_count = 0

    def build(self):
        try:
            if self.page and self.page.session:
                self.text = self.page.session.get("lang.home.tab.alarm")
        except:
            logging.exception('exception occured at AlarmButton.build')

    def handle_data(self):
        self.alarm_count = AlarmLog.select().where(AlarmLog.is_recovery == False).count()
        self.not_ack_count = AlarmLog.select().where(AlarmLog.acknowledge_time.is_null()).count()

    def set_normal_button(self):
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(10)),
            color=ft.Colors.INVERSE_SURFACE,
            bgcolor=ft.Colors.SURFACE
        )
        self.icon_color = ft.Colors.INVERSE_SURFACE

    def set_red_button(self):
        self.style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(10)),
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED
        )
        self.icon_color = ft.Colors.WHITE

    def toggle_badge(self):
        if self.page:
            if self.alarm_count > 0:
                self.badge = ft.Badge(
                    text=str(self.alarm_count), label_visible=True,
                    bgcolor=ft.Colors.RED, text_color=ft.Colors.WHITE
                )
            else:
                self.badge = None
            self.update()

    def toggle_button(self, blink: bool):
        try:
            if self.page:
                if blink:
                    self.set_red_button()
                else:
                    self.set_normal_button()
                self.update()
        except:
            logging.exception('exception occured at AlarmButton.toggle_button')


    async def __loop(self):
        cnt = 0
        while self.task_running:
            try:
                # 每隔5检查一下数据
                if cnt % 5 == 0:
                    self.handle_data()
                    self.toggle_badge()

                if self.not_ack_count > 0:
                    self.toggle_button(cnt % 2 == 0)

                cnt += 1
            except:
                logging.exception("exception occured at AlarmButton.__loop")
                self.task_running = False
                break
            finally:
                await asyncio.sleep(1)

    def did_mount(self):
        self.task = self.page.run_task(self.__loop)

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()
