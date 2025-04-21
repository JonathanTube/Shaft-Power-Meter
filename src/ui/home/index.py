import flet as ft
from common.public_controls import PublicControls
from ui.home.alarm.alarm_button import AlarmButton
from ui.home.alarm.alarm_list import AlarmList
from ui.home.counter.index import Counter
from ui.home.dashboard.index import Dashboard
from ui.home.event.event_button import EventButton
from ui.home.logs.index import Logs
from ui.home.propeller_curve.index import PropellerCurve
from ui.home.trendview.index import TrendView
from ui.home.event.event_list import EventList
from db.models.event_log import EventLog
from db.models.alarm_log import AlarmLog
from db.models.system_settings import SystemSettings


class Home(ft.Container):
    def __init__(self):
        super().__init__()
        self.system_settings = SystemSettings.get()
        self.current_index = 0

        self.default_button_style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(0)),
            color=ft.Colors.INVERSE_SURFACE
        )

        self.active_button_style = ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=ft.border_radius.all(0)),
            color=ft.Colors.PRIMARY,
        )

    def build(self):
        self.dashboard = ft.TextButton(
            text=self.page.session.get("lang.home.tab.dashboard"),
            icon=ft.Icons.DASHBOARD_OUTLINED,
            icon_color=ft.Colors.PRIMARY,
            style=self.active_button_style,
            on_click=lambda e: self.__on_click(e, 0)
        )
        self.counter = ft.TextButton(
            text=self.page.session.get("lang.home.tab.counter"),
            icon=ft.Icons.TIMER_OUTLINED,
            icon_color=ft.Colors.INVERSE_SURFACE,
            style=self.default_button_style,
            on_click=lambda e: self.__on_click(e, 1)
        )
        self.trendview = ft.TextButton(
            text=self.page.session.get("lang.home.tab.trendview"),
            icon=ft.Icons.TRENDING_UP_OUTLINED,
            icon_color=ft.Colors.INVERSE_SURFACE,
            style=self.default_button_style,
            on_click=lambda e: self.__on_click(e, 2)
        )
        self.propeller_curve = ft.TextButton(
            text=self.page.session.get("lang.home.tab.propeller_curve"),
            icon=ft.Icons.STACKED_LINE_CHART_OUTLINED,
            icon_color=ft.Colors.INVERSE_SURFACE,
            style=self.default_button_style,
            on_click=lambda e: self.__on_click(e, 3)
        )
        self.alarm_button = AlarmButton(on_click=lambda e: self.__on_click(e, 4))
        PublicControls.alarm_button = self.alarm_button

        self.event_button = EventButton(on_click=lambda e: self.__on_click(e, 5))
        print("====================================", self.event_button)
        PublicControls.event_button = self.event_button
        print("====================================", PublicControls.event_button)

        self.logs = ft.TextButton(
            text=self.page.session.get("lang.home.tab.logs"),
            icon=ft.Icons.HISTORY_OUTLINED,
            icon_color=ft.Colors.INVERSE_SURFACE,
            style=self.default_button_style,
            on_click=lambda e: self.__on_click(e, 6)
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
                    content=self.row_items,
                    height=40,
                    alignment=ft.alignment.center
                ),
                ft.Divider(thickness=1, height=1),
                self.main_container
            ]
        )

    def __on_click(self, e, index: int):
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

        self.update()

    def update_event_badge(self):
        count = EventLog.select().where(EventLog.breach_reason == None).count()
        if count > 0:
            self.event_button.badge = ft.Badge(
                text=str(count),
                bgcolor=ft.Colors.RED,
                text_color=ft.Colors.WHITE,
                label_visible=True
            )
        else:
            self.event_button.badge = None
        self.event_button.update()

    def update_alarm_badge(self):
        count = AlarmLog.select().where(AlarmLog.acknowledge_time == None).count()
        if count > 0:
            self.alarm_button.badge = ft.Badge(
                text=str(count),
                bgcolor=ft.Colors.RED,
                text_color=ft.Colors.WHITE,
                label_visible=True
            )
        else:
            self.alarm_button.badge = None
        self.alarm_button.update()

    def did_mount(self):
        self.update_event_badge()
        self.update_alarm_badge()

    def will_unmount(self):
        PublicControls.event_button = None
        PublicControls.alarm_button = None
