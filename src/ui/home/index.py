import asyncio
import logging
from random import random
import flet as ft
from common.control_manager import ControlManager
from common.global_data import gdata
from ui.home.alarm.alarm_button import AlarmButton
from ui.home.alarm.index import AlarmList
from ui.home.counter.index import Counter
from ui.home.dashboard.index import Dashboard
from ui.home.event.event_button import EventButton
from ui.home.logs.index import Logs
from ui.home.propeller_curve.index import PropellerCurve
from ui.home.trendview.index import TrendView
from ui.home.event.event_list import EventList
from db.models.system_settings import SystemSettings


class Home(ft.Container):
    def __init__(self):
        super().__init__()
        self.task_running = False
        self.task = None

        self.system_settings:SystemSettings = SystemSettings.get()
        self.current_index = 0

        self.default_button_style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(10)),
            color=ft.Colors.INVERSE_SURFACE
        )

        self.active_button_style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(10)),
            color=ft.Colors.PRIMARY,
            side=ft.border.all(2, ft.Colors.PRIMARY)
        )

    def build(self):
        self.dashboard = ft.TextButton(
            text=self.page.session.get("lang.home.tab.dashboard"),
            icon=ft.Icons.DASHBOARD_OUTLINED,
            icon_color=ft.Colors.PRIMARY,
            style=self.active_button_style,
            on_click=lambda e: self.__on_click(0)
        )
        self.counter = ft.TextButton(
            text=self.page.session.get("lang.home.tab.counter"),
            icon=ft.Icons.TIMER_OUTLINED,
            icon_color=ft.Colors.INVERSE_SURFACE,
            style=self.default_button_style,
            on_click=lambda e: self.__on_click(1)
        )
        self.trendview = ft.TextButton(
            text=self.page.session.get("lang.home.tab.trendview"),
            icon=ft.Icons.TRENDING_UP_OUTLINED,
            icon_color=ft.Colors.INVERSE_SURFACE,
            style=self.default_button_style,
            on_click=lambda e: self.__on_click(2)
        )
        self.propeller_curve = ft.TextButton(
            text=self.page.session.get("lang.home.tab.propeller_curve"),
            icon=ft.Icons.STACKED_LINE_CHART_OUTLINED,
            icon_color=ft.Colors.INVERSE_SURFACE,
            style=self.default_button_style,
            visible=self.system_settings.is_master and self.system_settings.display_propeller_curve,
            on_click=lambda e: self.__on_click(3)
        )
        self.alarm_button = AlarmButton(on_click=lambda e: self.__on_click(4))
        ControlManager.alarm_button = self.alarm_button
        self.event_button = EventButton(on_click=lambda e: self.__on_click(5))
        ControlManager.event_button = self.event_button

        self.logs = ft.TextButton(
            text=self.page.session.get("lang.home.tab.logs"),
            icon=ft.Icons.HISTORY_OUTLINED,
            icon_color=ft.Colors.INVERSE_SURFACE,
            style=self.default_button_style,
            on_click=lambda e: self.__on_click(6)
        )

        self.row_items = ft.Row(
            spacing=5,
            controls=[
                self.dashboard,
                self.counter,
                self.trendview,
                self.propeller_curve,
                self.alarm_button,
                self.event_button,
                self.logs
            ]
        )

        self.main_container = ft.Container(
            expand=True,
            content=Dashboard()
        )

        self.content = ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Container(
                    padding=ft.padding.only(left=10),
                    content=self.row_items,
                    height=40,
                    alignment=ft.alignment.center
                ),
                ft.Divider(thickness=1, height=1),
                self.main_container
            ]
        )

    def __on_click(self, index: int):
        try:
            if self.current_index == index:
                return

            self.current_index = index
            for idx, item in enumerate(self.row_items.controls):
                if idx == index:
                    item.style = self.active_button_style
                    item.icon_color = ft.Colors.PRIMARY
                else:
                    item.style = self.default_button_style
                    item.icon_color = ft.Colors.INVERSE_SURFACE
                if item and item.page:
                    item.update()

            if index == 0:
                self.main_container.content = Dashboard()
            elif index == 1:
                self.main_container.content = Counter()
            elif index == 2:
                self.main_container.content = TrendView()
            elif index == 3:
                self.main_container.content = PropellerCurve()
            elif index == 4:
                self.main_container.content = AlarmList()
            elif index == 5:
                self.main_container.content = EventList()
            elif index == 6:
                self.main_container.content = Logs()

            if self.main_container and self.main_container.page:
                self.main_container.update()
        except:
            logging.exception("exception occured at Home")

    def did_mount(self):
        self.task_running = True
        self.task = self.page.run_task(self.test_auto_run)
        if ControlManager.event_button and ControlManager.event_button.page:
            ControlManager.event_button.update_event()

        if ControlManager.alarm_button and ControlManager.alarm_button.page:
            ControlManager.alarm_button.update_alarm()

    def will_unmount(self):
        self.task_running = False
        if self.task:
            self.task.cancel()

        ControlManager.event_button = None
        ControlManager.alarm_button = None


    async def test_auto_run(self):
        while self.task_running and gdata.auto_testing:
            self.__on_click(int(random() * 10) % 7)
            await asyncio.sleep(random())
        self.task_running = False