import flet as ft
import os
from pathlib import Path
from ui.home.alarm.alarm_list import AlarmList
from ui.home.counter.index import Counter
from ui.home.dashboard.index import Dashboard
from ui.home.logs.index import Logs
from ui.home.propeller_curve.index import PropellerCurve
from ui.home.trendview.index import TrendView
from ui.home.event.event_list import EventList
from db.models.event_log import EventLog
from db.models.alarm_log import AlarmLog


class Home(ft.Stack):
    def __init__(self):
        super().__init__()

    def build(self):
        spacing = 2
        self.dashboard = ft.Tab(
            tab_content=ft.Row(spacing=spacing, controls=[
                ft.Icon(name=ft.Icons.DASHBOARD_OUTLINED),
                ft.Text("Dashboard")
            ]),
            content=Dashboard()
        )
        self.counter = ft.Tab(
            tab_content=ft.Row(spacing=spacing, controls=[
                ft.Icon(name=ft.Icons.TIMER_OUTLINED),
                ft.Text("Counter")
            ]),
            content=Counter()
        )
        self.trendview = ft.Tab(
            tab_content=ft.Row(spacing=spacing, controls=[
                ft.Icon(name=ft.Icons.TRENDING_UP_OUTLINED),
                ft.Text("TrendView")
            ]),
            content=TrendView()
        )
        self.propeller_curve = ft.Tab(
            tab_content=ft.Row(spacing=spacing, controls=[
                ft.Icon(name=ft.Icons.STACKED_LINE_CHART_OUTLINED),
                ft.Text("Propeller Curve")
            ]),
            content=PropellerCurve()
        )
        self.alarm = ft.Tab(
            tab_content=ft.Row(spacing=spacing, controls=[
                ft.Icon(name=ft.Icons.WARNING_OUTLINED),
                ft.Text("Alarm")
            ]),
            content=AlarmList()
        )

        self.event = ft.Tab(
            tab_content=ft.Row(spacing=spacing, controls=[
                ft.Icon(name=ft.Icons.EVENT_OUTLINED),
                ft.Text("Event")
            ]),
            content=EventList()
        )
        self.logs = ft.Tab(
            tab_content=ft.Row(spacing=spacing, controls=[
                ft.Icon(name=ft.Icons.HISTORY_OUTLINED),
                ft.Text("Logs")
            ]),
            content=Logs()
        )

        self.override_button = ft.FilledButton(
            top=8,
            right=20,
            text="Override",
            icon=ft.icons.NOTIFICATIONS_ON_OUTLINED,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED,
            color=ft.Colors.WHITE,
            visible=False,
            on_click=self.__on_override_button_click
        )

        self.controls = [
            ft.Tabs(
                # padding=50,
                selected_index=0,
                animation_duration=300,
                indicator_color=ft.Colors.PRIMARY,
                label_text_style=ft.TextStyle(
                    size=13,
                    weight=ft.FontWeight.W_600
                ),
                label_color=ft.Colors.PRIMARY,  # 选中时文本颜色
                unselected_label_color=ft.Colors.GREY_600,  # 未选中时文本颜色
                tabs=[
                    self.dashboard,
                    self.counter,
                    self.trendview,
                    self.propeller_curve,
                    self.alarm,
                    self.event,
                    self.logs
                ],
                expand=True
            ),
            self.override_button
        ]
        # create audio alarm
        base_dir = Path(__file__).parent.parent.parent
        audit_src = os.path.join(base_dir, "assets", "alarm.mp3")
        self.audio_alarm = ft.Audio(
            src=audit_src, autoplay=False, release_mode=ft.audio.ReleaseMode.LOOP)
        self.page.overlay.append(self.audio_alarm)

    def __update_event_badge(self):
        count = EventLog.select().where(EventLog.breach_reason == None).count()
        if count > 0:
            self.event.tab_content.controls[1].badge = ft.Badge(
                text=str(count),
                bgcolor=ft.Colors.RED,
                offset=ft.Offset(10, -10),
                text_color=ft.Colors.WHITE,
                label_visible=True
            )
        else:
            self.event.tab_content.controls[1].badge = None
        self.event.tab_content.controls[1].update()
        self.event.content.on_search(None, None)

    def __update_alarm_badge(self):
        count = AlarmLog.select().count()
        if count > 0:
            self.alarm.tab_content.controls[1].badge = ft.Badge(
                text=str(count),
                bgcolor=ft.Colors.RED,
                offset=ft.Offset(10, -10),
                text_color=ft.Colors.WHITE,
                label_visible=True
            )
        else:
            self.alarm.tab_content.controls[1].badge = None
        self.alarm.tab_content.controls[1].update()

    def __on_override_button_click(self, e):
        self.audio_alarm.pause()
        self.override_button.icon = ft.icons.NOTIFICATIONS_OFF_OUTLINED
        self.override_button.disabled = True
        self.override_button.bgcolor = ft.Colors.RED_400
        self.override_button.update()

    def __set_tab_text(self, tab: ft.Tab, code: str):
        tab.tab_content.controls[1].value = self.page.session.get(code)

    def on_breach_event_occured(self, topic: str, breach_event_occured: bool):
        # print(f"home on_breach_event_occured: {breach_event_occured}")
        if breach_event_occured:
            self.override_button.icon = ft.icons.NOTIFICATIONS_ON_OUTLINED
            self.override_button.bgcolor = ft.Colors.RED
            self.override_button.visible = True
            self.override_button.disabled = False
            self.audio_alarm.play()
        else:
            self.override_button.visible = False
            self.audio_alarm.pause()
            print("audio alarm paused")

        self.override_button.update()
        self.__update_event_badge()

    def did_mount(self):
        self.page.pubsub.subscribe_topic("breach_event_occured",
                                         self.on_breach_event_occured)
        self.set_language()
        self.__update_event_badge()
        self.__update_alarm_badge()

    def will_unmount(self):
        self.page.pubsub.unsubscribe_topic("breach_event_occured")

    def before_update(self):
        self.set_language()

    def set_language(self):
        self.__set_tab_text(self.dashboard, "lang.home.tab.dashboard")
        self.__set_tab_text(self.counter, "lang.home.tab.counter")
        self.__set_tab_text(self.trendview, "lang.home.tab.trendview")
        self.__set_tab_text(self.propeller_curve,
                            "lang.home.tab.propeller_curve")
        self.__set_tab_text(self.alarm, "lang.home.tab.alarm")
        self.__set_tab_text(self.event, "lang.home.tab.event")
        self.__set_tab_text(self.logs, "lang.home.tab.logs")
