import math
import flet as ft
import logging
from ui.common.simple_card import SimpleCard
from utils.unit_parser import UnitParser
from common.global_data import gdata
from db.models.preference import Preference
from db.models.system_settings import SystemSettings
from db.models.limitations import Limitations


class SinglePowerLine(ft.Container):
    def __init__(self):
        super().__init__()

        self.expand = True

        preference: Preference = Preference.get()
        self.system_unit = preference.system_unit

        system_settings: SystemSettings = SystemSettings.get()
        self.sha_po_li = system_settings.sha_po_li

        limitations: Limitations = Limitations.get()
        self.max_power = limitations.power_max

        if self.sha_po_li:
            self.threshold_power = system_settings.eexi_limited_power
        else:
            self.threshold_power = limitations.power_warning

    def build(self):
        try:
            self.data_line = ft.LineChartData(
                above_line_bgcolor=ft.Colors.SURFACE,
                curved=False,
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
                bottom_axis=ft.ChartAxis(labels_size=30, show_labels=True),
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
            self.__handle_bottom_axis()
            self.__handle_data_line()

            if self.threshold_filled:
                self.threshold_filled.data_points = self.get_threshold_data()
            
            if self.threshold_line:
                self.threshold_line.data_points = self.get_threshold_data()

            if self.chart and self.chart.page:
                self.chart.update()
        except:
            logging.exception('exception occured at SinglePowerLine.reload')

    def __handle_bottom_axis(self):
        try:
            labels = []
            for index, item in enumerate(gdata.sps_power_history):
                # 每隔6个数据点显示一个标签
                if index % 6 == 0:
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
            logging.exception('exception occured at SinglePowerLine.__handle_bottom_axis')


    def __handle_data_line(self):
        try:
            data_points = []
            for index in range(len(gdata.sps_power_history)):
                power_sps = gdata.sps_power_history[index][0]
                power_sps2 = 0
                try:
                    # print(f"gdata.sps2_power_history======================: {gdata.sps2_power_history}")
                    # print(f"index======================: {index}")
                    # print(f"gdata.sps2_power_history[index]================111======: {gdata.sps2_power_history[index]}")
                    power_sps2 = gdata.sps2_power_history[index][0]
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
            for index in range(len(gdata.sps_power_history)):
                data_points.append(ft.LineChartDataPoint(index, power_and_unit[0]))

            return data_points
        except:
            logging.exception('exception occured at SinglePowerLine.__handle_data_line')

        return []

