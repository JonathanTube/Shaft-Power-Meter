import flet as ft

from ui.home.alarm.index import createAlarm
from ui.home.counter.index import createCounter
from ui.home.dashboard.index import Dashboard
from ui.home.logs.index import Logs
from ui.home.notice.index import Notice
from ui.home.propeller_curve.index import CreatePropellerCurve
from ui.home.trendview.index import TrendView


class Home(ft.Stack):
    def __init__(self):
        super().__init__()
        tabs = self.__create_tabs()
        notice = Notice().create()
        self.controls = [tabs, notice]

    def __create_tab_content(self, content):
        return ft.Container(
            content=content,
            # padding=ft.padding.only(left=20, right=20, bottom=0, top=10),
            expand=True
        )

    def __create_tabs(self):
        spacing = 2
        return ft.Tabs(
            # padding=50,
            selected_index=0,
            animation_duration=300,
            indicator_color=ft.Colors.PRIMARY,
            label_color=ft.Colors.PRIMARY,  # 选中时文本颜色
            unselected_label_color=ft.Colors.GREY_600,  # 未选中时文本颜色
            tabs=[
                ft.Tab(
                    tab_content=ft.Row(spacing=spacing, controls=[
                        ft.Icon(name=ft.Icons.DASHBOARD_OUTLINED),
                        ft.Text("Dashboard")
                    ]),
                    content=self.__create_tab_content(Dashboard())
                ),
                ft.Tab(
                    tab_content=ft.Row(spacing=spacing, controls=[
                        ft.Icon(name=ft.Icons.TIMER_OUTLINED),
                        ft.Text("Counter")
                    ]),
                    content=self.__create_tab_content(createCounter(True))
                ),
                ft.Tab(
                    tab_content=ft.Row(spacing=spacing, controls=[
                        ft.Icon(name=ft.Icons.TRENDING_UP_OUTLINED),
                        ft.Text("TrendView")
                    ]),
                    content=self.__create_tab_content(TrendView())
                ),
                ft.Tab(
                    tab_content=ft.Row(spacing=spacing, controls=[
                        ft.Icon(name=ft.Icons.STACKED_LINE_CHART_OUTLINED),
                        ft.Text("Propeller Curve")
                    ]),
                    content=self.__create_tab_content(CreatePropellerCurve())
                ),
                ft.Tab(
                    tab_content=ft.Row(spacing=spacing, controls=[
                        ft.Icon(name=ft.Icons.ALARM_OUTLINED),
                        ft.Text("Alarm")
                    ]),
                    content=self.__create_tab_content(createAlarm())
                ),
                ft.Tab(
                    tab_content=ft.Row(spacing=spacing, controls=[
                        ft.Icon(name=ft.Icons.SECURITY_OUTLINED),
                        ft.Text("Logs")
                    ]),
                    content=self.__create_tab_content(Logs())
                )
            ],
            expand=True
        )
