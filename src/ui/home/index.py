import flet as ft
from ui.home.alarm.alarm_list import AlarmList
from ui.home.counter.index import Counter
from ui.home.dashboard.index import Dashboard
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

    def build(self):
        spacing = 2
        self.dashboard = ft.Tab(
            tab_content=ft.Row(spacing=spacing, controls=[
                ft.Icon(name=ft.Icons.DASHBOARD_OUTLINED),
                ft.Text(self.page.session.get("lang.home.tab.dashboard"))
            ]),
            content=Dashboard()
        )
        self.counter = ft.Tab(
            tab_content=ft.Row(spacing=spacing, controls=[
                ft.Icon(name=ft.Icons.TIMER_OUTLINED),
                ft.Text(self.page.session.get("lang.home.tab.counter"))
            ]),
            content=Counter()
        )
        self.trendview = ft.Tab(
            tab_content=ft.Row(spacing=spacing, controls=[
                ft.Icon(name=ft.Icons.TRENDING_UP_OUTLINED),
                ft.Text(self.page.session.get("lang.home.tab.trendview"))
            ]),
            content=TrendView()
        )
        self.propeller_curve = ft.Tab(
            tab_content=ft.Row(spacing=spacing, controls=[
                ft.Icon(name=ft.Icons.STACKED_LINE_CHART_OUTLINED),
                ft.Text(self.page.session.get("lang.home.tab.propeller_curve"))
            ]),
            content=PropellerCurve()
        )
        self.alarm = ft.Tab(
            tab_content=ft.Row(spacing=spacing, controls=[
                ft.Icon(name=ft.Icons.WARNING_OUTLINED),
                ft.Text(self.page.session.get("lang.home.tab.alarm"))
            ]),
            content=AlarmList()
        )

        self.event = ft.Tab(
            tab_content=ft.Row(spacing=spacing, controls=[
                ft.Icon(name=ft.Icons.EVENT_OUTLINED),
                ft.Text(self.page.session.get("lang.home.tab.event"))
            ]),
            content=EventList(),
            visible=self.system_settings.sha_po_li
        )
        self.logs = ft.Tab(
            tab_content=ft.Row(spacing=spacing, controls=[
                ft.Icon(name=ft.Icons.HISTORY_OUTLINED),
                ft.Text(self.page.session.get("lang.home.tab.logs"))
            ]),
            content=Logs()
        )

        self.content = ft.Tabs(
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
        )

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

    def __set_tab_text(self, tab: ft.Tab, code: str):
        tab.tab_content.controls[1].value = self.page.session.get(code)

    def on_breach_event_occured(self, topic: str, breach_event_occured: bool):
        if breach_event_occured:
            self.__update_event_badge()

    def did_mount(self):
        self.page.pubsub.subscribe_topic("breach_event_occured", self.on_breach_event_occured)
        self.__update_event_badge()
        self.__update_alarm_badge()

    def will_unmount(self):
        self.page.pubsub.unsubscribe_topic("breach_event_occured")