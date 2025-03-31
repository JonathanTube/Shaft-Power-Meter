import math
import flet as ft


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
                # Normal Propeller Curve
                ft.LineChartData(
                    color=ft.Colors.BLUE,
                    data_points=[]
                ),
                # Normal Propeller Curve star points
                ft.LineChartData(
                    data_points=[],
                    point=ft.ChartCirclePoint(
                        color=ft.Colors.RED,
                        radius=3
                    )
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
                    data_points=[],
                    point=ft.ChartCirclePoint(
                        color=ft.Colors.ORANGE,
                        radius=5
                    )
                ),
                # sps2
                ft.LineChartData(
                    data_points=[],
                    point=ft.ChartCirclePoint(
                        color=ft.Colors.LIME,
                        radius=5
                    )
                ),
                # MCR 100% Point
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(100, 100)
                    ],
                    point=ft.ChartCirclePoint(
                        color=ft.Colors.RED,
                        radius=8,
                        stroke_color=ft.Colors.RED,
                        stroke_width=1
                    )
                ),
            ]
        )

        self.content = self.chart

    def get_points(self, rpm_left, power_left, rpm_right, power_right, count=100):
        rpm = np.linspace(start=rpm_left, stop=rpm_right, num=count)

        # 如果左端点为0，0
        if rpm_left == 0 and power_left == 0:
            if power_right == 0:
                return [], []
            # 计算系数
            k = power_right / rpm_right**3
            # print('rpm=', rpm)
            power = k * rpm**3
            # 最后一位向上取整
            power[-1] = math.ceil(power[-1])

            return rpm, power
        else:
            diff = (rpm - rpm_left) / (rpm_right - rpm_left)
            power = power_left + diff ** 3 * (power_right - power_left)
            return rpm, power

    def update_static_data(self, normal_rpm_left: float, normal_power_left: float,
                           normal_rpm_right: float, normal_power_right: float,
                           normal_line_color: str,
                           light_propeller: float, light_propeller_line_color: str,
                           speed_limit: float, speed_limit_line_color: str,
                           torque_load_limit_rpm_left: float, torque_load_limit_power_left: float,
                           torque_load_limit_rpm_right: float, torque_load_limit_power_right: float,
                           torque_load_limit_line_color: str,
                           overload: float, overload_line_color: str):

        # 设置最小值, 如果左端点是0，就从0开始，否则从左端点*0.8开始
        self.chart.min_x = 0 if normal_rpm_left == 0 else normal_rpm_left * 0.8
        self.chart.min_y = 0 if normal_power_left == 0 else normal_power_left * 0.8

        rpm_points, power_points = self.get_points(
            normal_rpm_left, normal_power_left, normal_rpm_right, normal_power_right
        )
        if len(rpm_points) == 0 or len(power_points) == 0:
            return

        # normal propeller curve
        self.chart.data_series[0].data_points = [
            *[ft.LineChartDataPoint(x, y)
              for x, y in zip(rpm_points, power_points)],
            ft.LineChartDataPoint(105, 100)
        ]
        self.chart.data_series[0].color = normal_line_color

        # normal propeller curve key points for check
        self.chart.data_series[1].data_points = [
            ft.LineChartDataPoint(normal_rpm_left, normal_power_left)
            # ft.LineChartDataPoint(normal_rpm_right, normal_power_right)
        ]

        # light propeller curve
        self.chart.data_series[2].data_points = [
            ft.LineChartDataPoint(x, y * (100 - light_propeller)/100) for x, y in zip(rpm_points, power_points)
        ]
        self.chart.data_series[2].color = light_propeller_line_color

        # speed limit curve
        self.chart.data_series[3].data_points = [
            ft.LineChartDataPoint(speed_limit, 0)
        ]
        self.chart.data_series[3].color = speed_limit_line_color

        # torque/load limit curve
        self.chart.data_series[4].data_points = [
            ft.LineChartDataPoint(
                torque_load_limit_rpm_left,
                torque_load_limit_power_left
            ),
            ft.LineChartDataPoint(
                torque_load_limit_rpm_right,
                torque_load_limit_power_right
            )
        ]
        self.chart.data_series[4].color = torque_load_limit_line_color

        # overload curve
        data_series_5 = (ft.LineChartDataPoint(x, y * (100 + overload)/100)
                         for x, y in zip(rpm_points, power_points))
        last_power = power_points[-1] * (100 + overload)/100
        self.chart.data_series[5].data_points = [
            *data_series_5,
            ft.LineChartDataPoint(
                speed_limit, last_power)
        ]
        self.chart.data_series[5].color = overload_line_color
        self.chart.update()

    def update_dynamic_data_sps1(self, sps1_speed: float, sps1_power: float):
        self.chart.data_series[6].data_points = [
            ft.LineChartDataPoint(sps1_speed, sps1_power)
        ]
        self.chart.data_series[6].update()

    def update_dynamic_data_sps2(self, sps2_speed: float, sps2_power: float):
        self.chart.data_series[7].data_points = [
            ft.LineChartDataPoint(sps2_speed, sps2_power)
        ]
        self.chart.data_series[7].update()
