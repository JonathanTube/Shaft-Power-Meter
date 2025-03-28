import flet as ft

from ui.home.alarm.index import createAlarm
from ui.home.counter.index import createCounter
from ui.home.dashboard.index import Dashboard
from ui.home.logs.index import Logs
from ui.home.notice.index import Notice
from ui.home.propeller_curve.index import PropellerCurve
from ui.home.trendview.index import TrendView


class Home(ft.Stack):
    def __init__(self):
        super().__init__()

    def build(self):
        spacing = 2

        self.notice = Notice().create()

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
            content=createCounter(True)
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
            content=createAlarm()
        )
        self.logs = ft.Tab(
            tab_content=ft.Row(spacing=spacing, controls=[
                ft.Icon(name=ft.Icons.HISTORY_OUTLINED),
                ft.Text("Logs")
            ]),
            content=Logs()
        )

        self.controls = [self.notice,  ft.Tabs(
            # padding=50,
            selected_index=0,
            animation_duration=300,
            indicator_color=ft.Colors.PRIMARY,
            label_color=ft.Colors.PRIMARY,  # 选中时文本颜色
            unselected_label_color=ft.Colors.GREY_600,  # 未选中时文本颜色
            tabs=[
                self.dashboard,
                self.counter,
                self.trendview,
                self.propeller_curve,
                self.alarm,
                self.logs
            ],
            expand=True
        )]

    def __set_tab_text(self, tab: ft.Tab, code: str):
        tab.tab_content.controls[1].value = self.page.session.get(code)

    def did_mount(self):
        self.set_language()

    def before_update(self):
        self.set_language()

    def set_language(self):
        self.__set_tab_text(self.dashboard, "lang.home.tab.dashboard")
        self.__set_tab_text(self.counter, "lang.home.tab.counter")
        self.__set_tab_text(self.trendview, "lang.home.tab.trendview")
        self.__set_tab_text(self.propeller_curve, "lang.home.tab.propeller_curve")
        self.__set_tab_text(self.alarm, "lang.home.tab.alarm")
        self.__set_tab_text(self.logs, "lang.home.tab.logs")
