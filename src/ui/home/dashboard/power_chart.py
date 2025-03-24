import asyncio
import math
import flet as ft
import numpy as np
from db.models.system_settings import SystemSettings
from db.models.propeller_setting import PropellerSetting
from db.models.data_log import DataLog


class PowerChart(ft.Card):
    # data_points contains x and y values, x is time like '00:00', y is float
    def __init__(self):
        super().__init__()
        self.max_y = 0
        self.unit = ""
        self.threshold = 0

        self.data_list = []
        self.expand = True

        self.__load_settings()

    def build(self):
        self.width = self.page.window.width * 0.95
        border = ft.BorderSide(width=.5, color=ft.Colors.ON_INVERSE_SURFACE)
        self.chart = ft.LineChart(
            border=ft.Border(left=border, bottom=border,
                             right=border, top=border),
            min_y=0,
            max_y=self.max_y,
            left_axis=self.__get_left_axis(),
            bottom_axis=ft.ChartAxis(labels_size=30, labels=[], visible=False),
            data_series=self.__get_data_series()
        )

        self.content = ft.Container(
            padding=ft.padding.only(left=10, right=30, top=20, bottom=20),
            content=self.chart,
            expand=True
        )

    def __load_settings(self):
        system_settings = SystemSettings.get_or_none()
        if system_settings is None:
            return

        self.sha_po_li = system_settings.sha_po_li
        self.threshold = system_settings.eexi_limited_power

        propeller_settings = PropellerSetting.get_or_none()
        if propeller_settings is None:
            return
        shaft_power = propeller_settings.shaft_power_of_mcr_operating_point
        self.max_y = shaft_power

    def did_mount(self):
        asyncio.create_task(self.__load_data())

    async def __load_data(self):
        while True:
            data_logs = DataLog.select().order_by(DataLog.id.desc()).limit(10)
            data_list = []
            for data_log in data_logs:
                _power = data_log.power
                data_list.append(
                    [data_log.utc_time.strftime('%H:%M:%S'), _power]
                )
            self.data_list = data_list
            # print('data_list=', data_list)
            self.__update(data_list)
            await asyncio.sleep(1)

    def __update(self, data_list: list[list[str, float]]):
        self.data_list = data_list
        self.__handle_bottom_axis()
        self.__handle_data_line()
        # shapoli on
        if self.sha_po_li:
            self.__handle_filled_color()
            self.__handle_threshold_line()
        self.chart.update()

    def __get_data_series(self):
        # shapoli on
        if self.sha_po_li:
            return [
                ft.LineChartData(
                    color=ft.Colors.TRANSPARENT,
                    above_line_bgcolor=ft.Colors.TRANSPARENT if len(
                        self.data_list) == 0 else ft.Colors.RED,
                    data_points=[]
                ), ft.LineChartData(
                    above_line_bgcolor=ft.Colors.SURFACE,
                    curved=True,
                    stroke_width=1,
                    color=ft.Colors.LIGHT_GREEN,
                    data_points=[]
                ), ft.LineChartData(
                    color=ft.Colors.RED,
                    stroke_width=1,
                    data_points=[]
                )
            ]

        # shapoli off
        return [
            ft.LineChartData(
                above_line_bgcolor=ft.Colors.SURFACE,
                curved=True,
                stroke_width=1,
                color=ft.Colors.LIGHT_GREEN,
                data_points=[]
            )
        ]

    def __get_left_axis(self):
        labels = []
        step = self.max_y / 10
        print('step=', step)
        range_list = np.arange(0, self.max_y, step)
        if range_list[-1] < self.max_y:
            range_list = np.append(range_list, self.max_y)
        print('range_list=', range_list)
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

        self.chart.data_series[1].data_points = data_points

    def __handle_threshold_line(self):
        data_points = []
        for index in range(len(self.data_list)):
            data_points.append(ft.LineChartDataPoint(index, self.threshold))

        self.chart.data_series[2].data_points = data_points

    def __handle_filled_color(self):
        data_points = []
        for index in range(len(self.data_list)):
            data_points.append(ft.LineChartDataPoint(index, self.threshold))

        self.chart.data_series[0].data_points = data_points

        filled_color = ft.Colors.RED
        if len(self.data_list) == 0:
            filled_color = ft.Colors.TRANSPARENT
        self.chart.data_series[0].above_line_bgcolor = filled_color
