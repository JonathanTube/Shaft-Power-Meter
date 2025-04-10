import flet as ft

from db.models.data_log import DataLog
from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser


class SinglePowerLine(ft.Container):
    def __init__(self, name: str = "Power", max_y: int = 0, sha_po_li: bool = False, threshold: float = 0, unit: int = 0):
        super().__init__()

        self.expand = True

        self.unit = unit

        self.name = name
        _power_and_unit = UnitParser.parse_power(max_y, unit)
        self.max_y = _power_and_unit[0]
        self.unit_name = _power_and_unit[1]

        self.sha_po_li = sha_po_li
        self.threshold = UnitParser.parse_power(threshold, unit)[0]

        self.data_list = []

    def build(self):
        self.data_line = ft.LineChartData(
            above_line_bgcolor=ft.Colors.SURFACE,
            curved=True,
            stroke_width=1,
            color=ft.Colors.LIGHT_GREEN,
            data_points=[]
        )

        self.threshold_filled = ft.LineChartData(
            visible=self.sha_po_li,
            above_line_bgcolor=ft.Colors.RED,
            color=ft.Colors.TRANSPARENT,
            data_points=[]
        )

        self.threshold_line = ft.LineChartData(
            visible=self.sha_po_li,
            color=ft.Colors.RED,
            stroke_width=1,
            data_points=[]
        )

        border = ft.BorderSide(
            width=.5, color=ft.colors.with_opacity(0.15, ft.colors.INVERSE_SURFACE)
        )
        self.chart = ft.LineChart(
            min_y=0,
            max_y=int(self.max_y * 1.1),
            expand=True,
            border=ft.Border(left=border, bottom=border),
            left_axis=ft.ChartAxis(
                labels_size=50,
                labels=[
                    ft.ChartAxisLabel(value=0),
                    ft.ChartAxisLabel(value=self.max_y)
                ]),
            bottom_axis=ft.ChartAxis(
                labels_size=30,
                visible=False,
                labels_interval=10
            ),
            data_series=[
                self.threshold_filled,
                self.data_line,
                self.threshold_line
            ]
        )

        self.content = SimpleCard(
            title=self.name,
            body=ft.Container(
                content=self.chart,
                padding=ft.padding.only(right=30)
            ),
            text_center=True
        )

    def update(self, data_list: list[DataLog]):
        self.__handle_bottom_axis(data_list)
        self.__handle_data_line(data_list)
        self.threshold_filled.data_points = self.get_threshold_data(data_list)
        self.threshold_line.data_points = self.get_threshold_data(data_list)
        self.chart.update()

    def __handle_bottom_axis(self, data_list: list[DataLog]):
        labels = []
        for index, item in enumerate(data_list):
            label = ft.ChartAxisLabel(
                value=index,
                label=ft.Container(
                    content=ft.Text(value=item.utc_date_time.strftime('%H:%M:%S')),
                    padding=ft.padding.only(top=10)
                )
            )
            labels.append(label)
        # print(f'labels={labels}')
        self.chart.bottom_axis.labels = labels
        self.chart.bottom_axis.visible = len(labels) > 0

    def __handle_data_line(self, data_list: list[DataLog]):
        data_points = []
        for index, item in enumerate(data_list):
            _power = UnitParser.parse_power(item.power, self.unit)
            data_points.append(ft.LineChartDataPoint(index, _power[0]))

        self.data_line.data_points = data_points

    def get_threshold_data(self, data_list: list[DataLog]):
        data_points = []
        for index in range(len(data_list)):
            data_points.append(ft.LineChartDataPoint(index, self.threshold))

        return data_points

    def set_name(self, name: str):
        self.name = f"{name} ({self.unit_name})"
