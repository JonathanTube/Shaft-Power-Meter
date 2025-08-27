import logging
import flet as ft
import math
from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser
from common.global_data import gdata


class DualPowerLine(ft.Container):
    def __init__(self):
        super().__init__()

        self.sps_color = ft.Colors.ORANGE
        self.sps2_color = ft.Colors.BLUE

        self.expand = True

    def build(self):
        try:
            self.sps_data_series = ft.LineChartData(
                curved=False,
                stroke_width=2,
                color=self.sps_color,
                data_points=[]
            )
            self.sps2_data_series = ft.LineChartData(
                curved=False,
                stroke_width=2,
                color=self.sps2_color,
                data_points=[]
            )

            border = ft.BorderSide(width=.5, color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE))

            power_and_unit = UnitParser.parse_power(gdata.configLimitation.power_max, gdata.configPreference.system_unit)
            left_max = math.ceil(power_and_unit[0])
            left_unit = power_and_unit[1]

            self.chart = ft.LineChart(
                width=1000,
                expand=True,
                border=ft.Border(left=border, bottom=border),
                max_y=left_max,
                left_axis=ft.ChartAxis(
                    labels_size=len(str(left_max)) * 15,
                    title=ft.Text(left_unit),
                    labels=[
                        ft.ChartAxisLabel(value=0),
                        ft.ChartAxisLabel(value=left_max)
                    ]
                ),
                bottom_axis=ft.ChartAxis(labels_size=30, labels_interval=1, visible=False),
                data_series=[self.sps_data_series, self.sps2_data_series]
            )

            # self.chart_title = ft.Text(self.page.session.get("lang.common.power"), size=18, weight=ft.FontWeight.BOLD)
            if self.page.session:
                chart_top = ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    controls=[
                        # self.chart_title,
                        ft.Text(self.page.session.get("lang.common.sps"), color=self.sps_color),
                        ft.Text(self.page.session.get("lang.common.sps2"), color=self.sps2_color)
                    ])
                self.content = SimpleCard(body=ft.Column(controls=[chart_top, self.chart]))
        except:
            logging.exception('exception occured at DualPowerLine.build')

    def reload(self):
        try:
            if self.chart and self.chart.page:
                self.__handle_bottom_axis()
                self.__handle_data_line_sps()
                self.__handle_data_line_sps2()
                self.chart.update()
        except:
            logging.exception('exception occured at DualPowerLine.reload')

    def __handle_bottom_axis(self):
        try:
            labels = []
            for index, item in enumerate(gdata.configSPS.power_history):
                if len(item) > 1:
                    label = ft.ChartAxisLabel(
                        value=index,
                        label=ft.Container(
                            content=ft.Text(value=item[1].strftime('%H:%M:%S')),
                            padding=ft.padding.only(top=10)
                        )
                    )
                    labels.append(label)

            if self.chart and self.chart.bottom_axis:
                self.chart.bottom_axis.labels = labels
                self.chart.bottom_axis.visible = len(labels) > 0
                size = 8
                if len(labels) > size:
                    self.chart.bottom_axis.labels_interval = (len(labels) + size) // size
        except:
            logging.exception('exception occured at DualPowerLine.__handle_bottom_axis')

    def __handle_data_line_sps(self):
        try:
            data_points = []
            for index, item in enumerate(gdata.configSPS.power_history):
                if len(item) > 0:
                    _power = UnitParser.parse_power(item[0], gdata.configPreference.system_unit)
                    data_points.append(ft.LineChartDataPoint(index, _power[0]))

            if self.sps_data_series is not None:
                self.sps_data_series.data_points = data_points

        except:
            logging.exception('exception occured at DualPowerLine.__handle_data_line_sps')

    def __handle_data_line_sps2(self):
        try:
            data_points = []
            for index, item in enumerate(gdata.configSPS2.power_history):
                if len(item) > 0:
                    _power = UnitParser.parse_power(item[0], gdata.configPreference.system_unit)
                    data_points.append(ft.LineChartDataPoint(index, _power[0]))

            if self.sps2_data_series is not None:
                self.sps2_data_series.data_points = data_points

        except:
            logging.exception('exception occured at DualPowerLine.__handle_data_line_sps2')
