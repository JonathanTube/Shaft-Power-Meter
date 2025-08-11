import asyncio
import logging
import flet as ft
from typing import Callable
from peewee import fn, Case

from db.models.alarm_log import AlarmLog


class AlarmButton(ft.TextButton):
    def __init__(self, style: ft.ButtonStyle, on_click: Callable):
        super().__init__()
        self.icon = ft.Icons.WARNING_ROUNDED
        self.on_click = on_click

        self.task = None
        self.task_running = True

        self.alarm_count = 0
        self.not_ack_count = 0

        self.active = False

        self.style = style

    def build(self):
        try:
            if self.page and self.page.session:
                self.text = self.page.session.get("lang.home.tab.alarm")
        except:
            logging.exception('exception occured at AlarmButton.build')

    def handle_data(self):
        try:
            self.alarm_count = AlarmLog.select(fn.COUNT(AlarmLog.id)).where(AlarmLog.recovery_time.is_null()).scalar()
            self.not_ack_count = AlarmLog.select(fn.COUNT(AlarmLog.id)).where(AlarmLog.acknowledge_time.is_null()).scalar()
        except:
            logging.exception('exception occured at AlarmButton.handle_data')
            self.alarm_count = 0
            self.not_ack_count = 0

    def set_normal_button(self):
        try:
            self.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(10)),
                color=ft.Colors.INVERSE_SURFACE,
                bgcolor=ft.Colors.SURFACE
            )

            if self.active:
                self.style.side = ft.border.all(2, ft.Colors.PRIMARY)

            self.icon_color = ft.Colors.INVERSE_SURFACE
        except:
            logging.exception('exception occured at AlarmButton.set_normal_button')

    def set_red_button(self):
        try:
            self.style = ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(10)),
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED
            )

            if self.active:
                self.style.side = ft.border.all(2, ft.Colors.PRIMARY)

            self.icon_color = ft.Colors.WHITE
        except:
            logging.exception('exception occured at AlarmButton.set_red_button')

    def toggle_badge(self):
        try:
            if self.page:
                if self.alarm_count > 0:
                    self.badge = ft.Badge(
                        text=str(self.alarm_count), label_visible=True,
                        bgcolor=ft.Colors.RED, text_color=ft.Colors.WHITE
                    )
                else:
                    self.badge = None

                if self.page:
                    self.update()
        except:
            logging.exception('exception occured at AlarmButton.toggle_badge')

    def toggle_button(self, blink: bool):
        try:
            if self.page:
                if blink:
                    self.set_red_button()
                else:
                    self.set_normal_button()
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
                else:
                    self.set_normal_button()

                self.update()

                cnt += 1
            except:
                logging.exception("exception occured at AlarmButton.__loop")
                self.task_running = False
                break
            finally:
                await asyncio.sleep(1)

    def did_mount(self):
        if self.page:
            self.task = self.page.run_task(self.__loop)

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()
