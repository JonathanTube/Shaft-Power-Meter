import flet as ft
from db.models.data_log import DataLog
from utils.unit_parser import UnitParser
from db.models.preference import Preference


class TrendviewChart(ft.Container):
    def __init__(self, name: str):
        super().__init__()

        self.name = name
        self.power_color = ft.Colors.ORANGE
        self.speed_color = ft.Colors.BLUE

        self.expand = True
        self.padding = 10
        self.border = ft.border.all(width=0.5, color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE))

        preference: Preference = Preference.get()
        self.unit = preference.system_unit

    def build(self):
        self.speed_data_series = ft.LineChartData(curved=False, stroke_width=2, color=self.speed_color, data_points=[])
        self.power_data_series = ft.LineChartData(curved=False, stroke_width=2, color=self.power_color, data_points=[])
        border = ft.BorderSide(width=.5, color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE))

        self.chart = ft.LineChart(
            expand=True,
            min_y=0,
            border=ft.Border(left=border, bottom=border, right=border),
            left_axis=ft.ChartAxis(title=ft.Text("rpm"), labels_size=40, labels=[]),
            right_axis=ft.ChartAxis(title=ft.Text("kW" if self.unit == 0 else "sHp"), title_size=25, labels_size=40, labels=[]),
            bottom_axis=ft.ChartAxis(title=ft.Text("UTC DateTime"), labels_size=40, labels=[]),
            data_series=[self.speed_data_series, self.power_data_series]
        )
        self.content = ft.Column(
            expand=True,
            controls=[
                ft.Text(self.name, size=18, weight=ft.FontWeight.W_500),
                self.chart
            ]
        )

    def reload(self, start_date: str, end_date: str):
        data_logs = DataLog.select(
            DataLog.power,
            DataLog.speed,
            DataLog.utc_date_time
        ).where(
            DataLog.name == self.name
        ).where(
            DataLog.utc_date_time >= start_date, DataLog.utc_date_time <= end_date
        ).order_by(
            DataLog.id.desc()
        )

        self.__handle_bottom_axis(data_logs)
        self.__handle_data_line_speed(data_logs)
        self.__handle_data_line_power(data_logs)
        self.chart.update()

    def __handle_bottom_axis(self, data_logs: list[DataLog]):
        labels = []
        for index, item in enumerate(data_logs):
            label = ft.ChartAxisLabel(
                value=index,
                label=ft.Container(
                    content=ft.Text(value=item.utc_date_time.strftime('%y-%m-%d')),
                    padding=ft.padding.only(top=10)
                )
            )
            labels.append(label)
        self.chart.bottom_axis.labels = labels
        self.chart.bottom_axis.visible = len(labels) > 0
        size = 5
        if len(labels) > size:
            self.chart.bottom_axis.labels_interval = (len(labels) + size) // size

    def __handle_data_line_speed(self, data_logs: list[DataLog]):
        data_points = []
        max_speed = 0
        for index, item in enumerate(data_logs):
            speed_and_unit = UnitParser.parse_speed(item.speed)
            data_points.append(ft.LineChartDataPoint(index, speed_and_unit[0]))
            if speed_and_unit[0] > max_speed:
                max_speed = speed_and_unit[0]
        self.speed_data_series.data_points = data_points
        print('max_speed=', max_speed)
        self.chart.left_axis.labels = [
            ft.ChartAxisLabel(value=0),
            ft.ChartAxisLabel(value=max_speed)
        ]

    def __handle_data_line_power(self, data_logs: list[DataLog]):
        data_points = []
        max_power = 0
        for index, item in enumerate(data_logs):
            power_and_unit = UnitParser.parse_power(item.power, self.unit, shrink=False)
            data_points.append(ft.LineChartDataPoint(index, power_and_unit[0]))
            if power_and_unit[0] > max_power:
                max_power = power_and_unit[0]
            self.chart.right_axis.title.value = power_and_unit[1]
        self.power_data_series.data_points = data_points
        print('max_power=', max_power)
        self.chart.right_axis.labels = [
            ft.ChartAxisLabel(value=0),
            ft.ChartAxisLabel(value=max_power)
        ]
