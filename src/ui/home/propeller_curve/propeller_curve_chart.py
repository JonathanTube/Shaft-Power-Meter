import math
import flet as ft
import numpy as np


class PropellerCurveChart(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = ft.padding.only(right=5)

    def build(self):
        border = ft.BorderSide(width=.5, color=ft.Colors.with_opacity(
            0.15, ft.Colors.INVERSE_SURFACE))

        self.chart = ft.LineChart(
            expand=True,
            interactive=False,
            vertical_grid_lines=ft.ChartGridLines(
                color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE),
                width=1
            ),
            horizontal_grid_lines=ft.ChartGridLines(
                color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE),
                width=1
            ),
            min_y=0,
            max_y=110,
            min_x=0,
            max_x=110,
            border=ft.Border(left=border, bottom=border,
                             right=border, top=border),
            left_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text("Engine shaft power, % of A"),
                title_size=30,
                labels=[
                    ft.ChartAxisLabel(value=0),
                    ft.ChartAxisLabel(value=110)
                ],
                labels_interval=10
            ),
            bottom_axis=ft.ChartAxis(
                labels_size=40,
                title=ft.Text("Engine speed, % of A"),
                title_size=30,
                labels=[
                    ft.ChartAxisLabel(value=0),
                    ft.ChartAxisLabel(value=110)
                ],
                labels_interval=10
            ),
            data_series=[
                # MCR 100% Point
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(100, 100)
                    ],
                    point=ft.ChartCirclePoint(
                        color=ft.Colors.RED,
                        radius=6,
                        stroke_color=ft.Colors.RED,
                        stroke_width=1
                    )
                ),
                # Normal Propeller Curve
                ft.LineChartData(
                    color=ft.Colors.BLUE,
                    data_points=[]
                ),
                # Light Propeller Curve
                ft.LineChartData(
                    dash_pattern=[10, 5],
                    color=ft.Colors.BLUE,
                    data_points=[]
                ),
                # Speed Limit Curve
                ft.LineChartData(
                    above_line=ft.ChartPointLine(
                        color=ft.Colors.RED,
                        dash_pattern=[2, 5],
                        width=2
                    ),
                    data_points=[]
                ),
                # Torque/Load Limit Curve
                ft.LineChartData(
                    color=ft.Colors.GREEN,
                    data_points=[]
                ),
                # Overload Curve
                ft.LineChartData(
                    dash_pattern=[10, 5],
                    color=ft.Colors.RED,
                    data_points=[]
                ),
                # sps1
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(80, 80)
                    ],
                    point=ft.ChartCirclePoint(
                        color=ft.Colors.BLUE,
                        radius=6,
                        stroke_color=ft.Colors.BLUE,
                        stroke_width=1
                    )
                ),
                # sps2
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(90, 90)
                    ],
                    point=ft.ChartCirclePoint(
                        color=ft.Colors.GREEN,
                        radius=6,
                        stroke_color=ft.Colors.GREEN,
                        stroke_width=1
                    )
                )
            ]
        )

        self.content = self.chart

    def get_points(self, rpm_left, power_left, rpm_right, power_right, count=100):
        k = power_left / rpm_left**3

        rpm = np.linspace(start=0, stop=rpm_right, num=count)
        # print('rpm=', rpm)
        power = k * rpm**3
        # 最后一位向上取整
        power[-1] = math.ceil(power[-1])

        return rpm, power

    def set_normal_propeller_curve(self, rpm_left, power_left,
                                   rpm_right, power_right,
                                   light_propeller_curve_below_radio: float, speed_limit_curve_ratio_of_rpm_of_mcr: float, overload_curve_ratio_of_rpm_of_mcr: float):
        rpm_points, power_points = self.get_points(
            rpm_left, power_left, rpm_right, power_right)

        # normal propeller curve
        self.chart.data_series[1].data_points = [
            *[ft.LineChartDataPoint(x, y)
              for x, y in zip(rpm_points, power_points)],
            ft.LineChartDataPoint(105, 100)
        ]

        # light propeller curve
        self.chart.data_series[2].data_points = [
            ft.LineChartDataPoint(x, y * (1 - light_propeller_curve_below_radio)) for x, y in zip(rpm_points, power_points)
        ]

        # speed limit curve
        self.chart.data_series[3].data_points = [
            ft.LineChartDataPoint(speed_limit_curve_ratio_of_rpm_of_mcr, 0)
        ]

        # torque/load limit curve
        self.chart.data_series[4].data_points = [
            ft.LineChartDataPoint(10, 20),
            ft.LineChartDataPoint(20, 30),
            ft.LineChartDataPoint(30, 40),
            ft.LineChartDataPoint(40, 50),
            ft.LineChartDataPoint(50, 60),
        ]
        # overload curve
        data_series_5 = (ft.LineChartDataPoint(x, y * (1 + overload_curve_ratio_of_rpm_of_mcr))
                         for x, y in zip(rpm_points, power_points))
        last_power = power_points[-1] * \
            (1 + overload_curve_ratio_of_rpm_of_mcr)
        self.chart.data_series[5].data_points = [
            *data_series_5,
            ft.LineChartDataPoint(
                speed_limit_curve_ratio_of_rpm_of_mcr, last_power)
        ]
        self.chart.update()
