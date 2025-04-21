import flet as ft

from db.models.data_log import DataLog
from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser


class DualPowerLine(ft.Container):
    def __init__(self, max_y: int = 0, unit: int = 0):
        super().__init__()

        self.max_y = UnitParser.parse_power(max_y, unit)[0]
        self.unit = unit

        self.sps1_color = ft.Colors.ORANGE
        self.sps2_color = ft.Colors.BLUE

        self.expand = True

    def __on_select(self, e, name):
        color = ft.Colors.WHITE if e.data == "true" else ft.Colors.INVERSE_SURFACE
        visible = e.data == "true"

        if name == "sps1":
            self.sps1_data_series.visible = visible
            self.menu_sps1.label.color = color
            self.menu_sps1.check_color = color
        elif name == "sps2":
            self.sps2_data_series.visible = visible
            self.menu_sps2.label.color = color
            self.menu_sps2.check_color = color

        self.menus.update()

    def __create_menus(self):
        self.menu_sps1 = ft.Chip(
            label=ft.Text("sps1", color=ft.Colors.WHITE),
            selected_color=self.sps1_color,
            selected=True,
            check_color=ft.Colors.WHITE,
            on_select=lambda e: self.__on_select(e, "sps1")
        )
        self.menu_sps2 = ft.Chip(
            label=ft.Text("sps2", color=ft.Colors.WHITE),
            selected_color=self.sps2_color,
            selected=True,
            check_color=ft.Colors.WHITE,
            on_select=lambda e: self.__on_select(e, "sps2")
        )
        self.menus = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[self.menu_sps1, self.menu_sps2],
            spacing=10
        )

    def build(self):
        self.__create_menus()

        self.sps1_data_series = ft.LineChartData(
            curved=True,
            stroke_width=2,
            color=self.sps1_color,
            data_points=[]
        )
        self.sps2_data_series = ft.LineChartData(
            curved=True,
            stroke_width=2,
            color=self.sps2_color,
            data_points=[]
        )

        border = ft.BorderSide(width=.5, color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE))

        self.chart = ft.LineChart(
            expand=True,
            border=ft.Border(left=border, bottom=border),
            left_axis=ft.ChartAxis(labels_size=50, labels=[
                ft.ChartAxisLabel(value=0),
                ft.ChartAxisLabel(value=self.max_y)
            ]),
            right_axis=ft.ChartAxis(labels_size=50),
            bottom_axis=ft.ChartAxis(
                labels_size=30, labels=[], visible=False, labels_interval=10),
            data_series=[self.sps1_data_series, self.sps2_data_series]
        )

        self.chart_title = ft.Text(self.page.session.get("lang.common.power"), size=18, weight=ft.FontWeight.BOLD)
        chart_top = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            controls=[
                self.chart_title,
                ft.Text("sps1", color=self.sps1_color),
                ft.Text("sps2", color=self.sps2_color)
            ])
        self.content = SimpleCard(
            body=ft.Column(controls=[chart_top, self.chart])
        )

    def set_data(self, data_list_sps1: list[DataLog], data_list_sps2: list[DataLog]):
        self.__handle_bottom_axis(data_list_sps1)
        self.__handle_data_line_sps1(data_list_sps1)
        self.__handle_data_line_sps2(data_list_sps2)
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

    def __handle_data_line_sps1(self, data_list: list[DataLog]):
        data_points = []
        for index, item in enumerate(data_list):
            _power = UnitParser.parse_power(item.power, self.unit)
            data_points.append(ft.LineChartDataPoint(index, _power[0]))

        self.sps1_data_series.data_points = data_points

    def __handle_data_line_sps2(self, data_list: list[DataLog]):
        data_points = []
        for index, item in enumerate(data_list):
            _power = UnitParser.parse_power(item.power, self.unit)
            data_points.append(ft.LineChartDataPoint(index, _power[0]))

        self.sps2_data_series.data_points = data_points