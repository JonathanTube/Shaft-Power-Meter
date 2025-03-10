import flet as ft
from ui.home.dashboard.index import createDashboard
from ui.home.counter.index import createCounter
from ui.home.trendview.index import createTrendView
from ui.home.propeller_curve.index import CreatePropellerCurve
from ui.home.alarm.index import createAlarm
from ui.home.logs.index import createLogs


def _tab_content(content):
    return ft.Container(
        content=content,
        padding=ft.padding.only(left=20, right=20, bottom=0, top=10),
        expand=True
    )


def createHome():
    return ft.Tabs(
        selected_index=0,
        animation_duration=300,
        indicator_color=ft.Colors.PRIMARY,
        label_color=ft.Colors.PRIMARY,  # 选中时文本颜色
        unselected_label_color=ft.Colors.GREY_600,  # 未选中时文本颜色
        tabs=[
            ft.Tab(
                tab_content=ft.Row(controls=[
                    ft.Icon(name=ft.Icons.DASHBOARD_OUTLINED),
                    ft.Text("Dashboard")
                ]),
                content=_tab_content(content=createDashboard())
            ),
            ft.Tab(
                tab_content=ft.Row(controls=[
                    ft.Icon(name=ft.Icons.TIMER_OUTLINED),
                    ft.Text("Counter")
                ]),
                content=_tab_content(createCounter(True))
            ),
            ft.Tab(
                tab_content=ft.Row(controls=[
                    ft.Icon(name=ft.Icons.TRENDING_UP_OUTLINED),
                    ft.Text("TrendView")
                ]),
                content=_tab_content(createTrendView())
            ),
            ft.Tab(
                tab_content=ft.Row(controls=[
                    ft.Icon(name=ft.Icons.STACKED_LINE_CHART_OUTLINED),
                    ft.Text("Propeller Curve")
                ]),
                content=_tab_content(CreatePropellerCurve())
            ),
            ft.Tab(
                tab_content=ft.Row(controls=[
                    ft.Icon(name=ft.Icons.ALARM_OUTLINED),
                    ft.Text("Alarm")
                ]),
                content=_tab_content(createAlarm())
            ),
            ft.Tab(
                tab_content=ft.Row(controls=[
                    ft.Icon(name=ft.Icons.EMERGENCY_RECORDING_OUTLINED),
                    ft.Text("Logs")
                ]),
                content=_tab_content(createLogs())
            )
        ],
        expand=True
    )
