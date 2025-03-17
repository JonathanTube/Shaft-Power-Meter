import flet as ft

from .alarm.index import createAlarm
from .counter.index import createCounter
from .dashboard.index import create_dashboard
from .logs.index import createLogs
from .notice.index import Notice
from .propeller_curve.index import CreatePropellerCurve
from .trendview.index import createTrendView


def __create_tab_content(content):
    return ft.Container(
        content=content,
        # padding=ft.padding.only(left=20, right=20, bottom=0, top=10),
        expand=True
    )


def __create_tabs():
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
                content=__create_tab_content(content=create_dashboard())
            ),
            ft.Tab(
                tab_content=ft.Row(spacing=spacing, controls=[
                    ft.Icon(name=ft.Icons.TIMER_OUTLINED),
                    ft.Text("Counter")
                ]),
                content=__create_tab_content(createCounter(True))
            ),
            ft.Tab(
                tab_content=ft.Row(spacing=spacing, controls=[
                    ft.Icon(name=ft.Icons.TRENDING_UP_OUTLINED),
                    ft.Text("TrendView")
                ]),
                content=__create_tab_content(createTrendView())
            ),
            ft.Tab(
                tab_content=ft.Row(spacing=spacing, controls=[
                    ft.Icon(name=ft.Icons.STACKED_LINE_CHART_OUTLINED),
                    ft.Text("Propeller Curve")
                ]),
                content=__create_tab_content(CreatePropellerCurve())
            ),
            ft.Tab(
                tab_content=ft.Row(spacing=spacing, controls=[
                    ft.Icon(name=ft.Icons.ALARM_OUTLINED),
                    ft.Text("Alarm")
                ]),
                content=__create_tab_content(createAlarm())
            )
            # ft.Tab(
            #     tab_content=ft.Row(spacing=spacing, controls=[
            #         ft.Icon(name=ft.Icons.EMERGENCY_RECORDING_OUTLINED),
            #         ft.Text("Logs")
            #     ]),
            #     content=__create_tab_content(createLogs())
            # )
        ],
        expand=True
    )


def create_home():
    return ft.Stack(controls=[
        __create_tabs(),
        Notice().create()
    ])
