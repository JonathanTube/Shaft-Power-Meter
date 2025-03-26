import flet as ft
import numpy as np


class PowerLineChart(ft.Container):
    def __init__(self, max_y: float = 0, sha_po_li: bool = False, threshold: float = 0):
        super().__init__()
        self.sha_po_li = sha_po_li
        self.threshold = threshold
        self.max_y = max_y

        self.data_list = []

        # set outline style
        self.border_radius = ft.border_radius.all(10)
        self.expand = True

    def build(self):
        border = ft.BorderSide(width=.5, color=ft.colors.with_opacity(
            0.15, ft.colors.INVERSE_SURFACE))
        self.chart = ft.LineChart(
            expand=True,
            border=ft.Border(left=border, bottom=border),
            min_y=0,
            max_y=self.max_y,
            left_axis=self.__get_left_axis(),
            bottom_axis=ft.ChartAxis(labels_size=30, labels=[], visible=False),
            data_series=self.__get_data_series()
        )

        self.content = ft.Container(
            padding=ft.padding.only(left=10, right=28, top=20, bottom=0),
            content=self.chart,
            expand=True
        )

    def update(self, data_list: list[list[str, float]]):
        self.data_list = data_list
        self.__handle_bottom_axis()
        self.__handle_data_line()
        # shapoli on
        if self.sha_po_li:
            self.__handle_filled_color()
            self.__handle_threshold_line()
        self.chart.update()

    def __get_data_series(self):
        self.data_series_line = ft.LineChartData(
            curved=True,
            stroke_width=1,
            color=ft.Colors.LIGHT_GREEN,
            data_points=[]
        )

        # shapoli on
        if self.sha_po_li:
            self.data_series_line.above_line_bgcolor = ft.Colors.SURFACE

            self.data_series_filled = ft.LineChartData(
                color=ft.Colors.TRANSPARENT,
                data_points=[]
            )

            if self.sha_po_li and len(self.data_list) > 0:
                self.data_series_filled.data_series_filled = ft.Colors.RED

            self.data_series_threshold = ft.LineChartData(
                color=ft.Colors.RED,
                stroke_width=1,
                data_points=[]
            )
            return [
                self.data_series_filled,
                self.data_series_line,
                self.data_series_threshold
            ]
        # shapoli off
        return [
            self.data_series_line
        ]

    def __get_left_axis(self):
        labels = []
        if self.max_y > 0:
            step = self.max_y / 10
            # print('step=', step)
            range_list = np.arange(0, self.max_y, step)
            if range_list[-1] < self.max_y:
                range_list = np.append(range_list, self.max_y)
                # print('range_list=', range_list)
                # TODO: get unit from system settings
                self.unit = 'kW'
                for value in range_list:
                    label = ft.Text(f"{value/1000:.1f}{self.unit}")
                    cal = ft.ChartAxisLabel(value=value, label=label)
                    labels.append(cal)
        # print(f'labels={labels}')
        return ft.ChartAxis(labels=labels, labels_size=50)

    def __handle_bottom_axis(self):
        labels = []
        for index, item in enumerate(self.data_list):
            cal = ft.ChartAxisLabel(
                value=index,
                label=ft.Container(
                    content=ft.Text(value=item[0]),
                    padding=ft.padding.only(top=10)
                )
            )
            labels.append(cal)

        self.chart.bottom_axis.labels = labels
        self.chart.bottom_axis.visible = len(labels) > 0

    def __handle_data_line(self):
        data_points = []
        for index, item in enumerate(self.data_list):
            data_points.append(ft.LineChartDataPoint(index, item[1]))

        self.data_series_line.data_points = data_points

    def __handle_threshold_line(self):
        data_points = []
        for index in range(len(self.data_list)):
            data_points.append(ft.LineChartDataPoint(index, self.threshold))

        self.data_series_threshold.data_points = data_points

    def __handle_filled_color(self):
        data_points = []
        for index in range(len(self.data_list)):
            data_points.append(ft.LineChartDataPoint(index, self.threshold))

        self.data_series_filled.data_points = data_points

        filled_color = ft.Colors.RED
        if len(self.data_list) == 0:
            filled_color = ft.Colors.TRANSPARENT
        self.data_series_filled.above_line_bgcolor = filled_color
