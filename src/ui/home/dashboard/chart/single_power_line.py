import math
import flet as ft
import logging
from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser
from common.global_data import gdata


class SinglePowerLine(ft.Container):
    def __init__(self):
        super().__init__()

        self.expand = True

        self.chart = None

        self.system_unit = gdata.configPreference.system_unit
        self.threshold_power = gdata.configCommon.eexi_limited_power
        self.max_power = gdata.configCommon.unlimited_power

    def build(self):
        try:
            if not gdata.configCommon.shapoli:
                self.threshold_power = gdata.configLimitation.power_warning
                self.max_power = gdata.configLimitation.power_max

            self.data_line = ft.LineChartData(
                above_line_bgcolor=ft.Colors.SURFACE,
                curved=False,
                stroke_width=1,
                color=ft.Colors.LIGHT_GREEN,
                data_points=[]
            )

            self.threshold_filled = ft.LineChartData(
                visible=gdata.configCommon.shapoli,
                above_line_bgcolor=ft.Colors.RED,
                color=ft.Colors.TRANSPARENT,
                data_points=[]
            )

            self.threshold_line = ft.LineChartData(
                visible=gdata.configCommon.shapoli,
                color=ft.Colors.RED,
                stroke_width=1,
                data_points=[]
            )

            border = ft.BorderSide(width=.5, color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE))

            power_and_unit = UnitParser.parse_power(self.max_power, self.system_unit)
            left_max = math.ceil(power_and_unit[0])
            left_unit = power_and_unit[1]

            width = 1000

            if self.page and self.page.window:
                width = self.page.window.width - 80

            self.chart = ft.LineChart(
                width=width,
                min_y=0,
                max_y=left_max,
                bgcolor=ft.Colors.translate,
                tooltip_fit_inside_horizontally=True,
                tooltip_fit_inside_vertically=True,
                expand=True,
                border=ft.Border(left=border, bottom=border),
                left_axis=ft.ChartAxis(
                    title=ft.Text(left_unit),
                    labels_interval=left_max / 5,
                    labels_size=len(str(left_max)) * 15,
                    labels=[
                        ft.ChartAxisLabel(value=0),
                        ft.ChartAxisLabel(value=left_max)
                    ]),
                bottom_axis=ft.ChartAxis(show_labels=False),
                data_series=[
                    self.threshold_filled,
                    self.data_line,
                    self.threshold_line
                ]
            )

            if self.page and self.page.session:
                self.content = SimpleCard(
                    title=self.page.session.get("lang.common.power"),
                    body=ft.Container(
                        content=self.chart,
                        padding=ft.padding.only(right=30)
                    ),
                    text_center=True
                )
        except:
            logging.exception('exception occured at SinglePowerLine.reload')

    def reload(self):
        try:
            self.__handle_data_line()

            if self.threshold_filled:
                self.threshold_filled.data_points = self.get_threshold_data()

            if self.threshold_line:
                self.threshold_line.data_points = self.get_threshold_data()

            if self.chart and self.chart.page:
                self.chart.update()
        except:
            logging.exception('exception occured at SinglePowerLine.reload')

    def __handle_data_line(self):
        try:
            data_points = []
            for index in range(len(gdata.configSPS.power_history)):
                power_sps = gdata.configSPS.power_history[index][0]
                power_sps2 = 0
                if gdata.configCommon.is_twins:
                    try:
                        power_sps2 = gdata.configSPS2.power_history[index][0]
                    except IndexError:
                        # 这里有可能是单浆，不处理
                        power_sps2 = 0

                power = power_sps + power_sps2
                if power > self.max_power:
                    power = self.max_power

                power_and_unit = UnitParser.parse_power(power, self.system_unit)
                data_points.append(ft.LineChartDataPoint(index, power_and_unit[0]))

            if self.data_line:
                self.data_line.data_points = data_points

        except:
            logging.exception('exception occured at SinglePowerLine.__handle_data_line')

    def get_threshold_data(self):
        try:
            data_points = []
            power_and_unit = UnitParser.parse_power(self.threshold_power, self.system_unit)
            for index in range(len(gdata.configSPS.power_history)):
                data_points.append(ft.LineChartDataPoint(index, power_and_unit[0]))

            return data_points
        except:
            logging.exception('exception occured at SinglePowerLine.__handle_data_line')

        return []
