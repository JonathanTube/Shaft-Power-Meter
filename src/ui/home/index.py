import flet as ft
from ui.home.dashboard.index import createDashboard
from ui.home.counter.index import createCounter
from ui.home.trendview.index import createTrendview
from ui.home.propeller_curve.index import CreatePropellerCurve
from ui.home.alarm.index import createAlarm
from ui.home.logs.index import createLogs


def createHome():
    return ft.Tabs(
        selected_index=0,
        animation_duration=300,
        indicator_color=ft.colors.PRIMARY,
        label_color=ft.colors.PRIMARY,  # 选中时文本颜色
        unselected_label_color=ft.colors.GREY_600,  # 未选中时文本颜色
        tabs=[
            ft.Tab(
                # text="Dashboard",
                # icon=ft.Icons.DASHBOARD_OUTLINED,
                tab_content=ft.Row(controls=[
                    ft.Icon(name=ft.Icons.DASHBOARD_OUTLINED),
                    ft.Text("Dashboard")
                ]),
                content=createDashboard(),
            ),
            ft.Tab(
                tab_content=ft.Row(controls=[
                    ft.Icon(name=ft.Icons.TIMER_OUTLINED),
                    ft.Text("Counter")
                ]),
                content=createCounter(),
            ),
            ft.Tab(
                tab_content=ft.Row(controls=[
                    ft.Icon(name=ft.Icons.TRENDING_UP_OUTLINED),
                    ft.Text("TrendView")
                ]),
                content=createTrendview(),
            ),
            ft.Tab(
                tab_content=ft.Row(controls=[
                    ft.Icon(name=ft.Icons.STACKED_LINE_CHART_OUTLINED),
                    ft.Text("Propeller Curve")
                ]),
                content=CreatePropellerCurve(),
            ),
            ft.Tab(
                tab_content=ft.Row(controls=[
                    ft.Icon(name=ft.Icons.ALARM_OUTLINED),
                    ft.Text("Alarm")
                ]),
                content=createAlarm(),
            ),
            ft.Tab(
                tab_content=ft.Row(controls=[
                    ft.Icon(name=ft.Icons.EMERGENCY_RECORDING_OUTLINED),
                    ft.Text("Logs")
                ]),
                content=createLogs(),
            )
        ],
        expand=1
    )
