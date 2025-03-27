import math
import flet as ft
import matplotlib
from matplotlib import pyplot as plt
from db.models.data_log import DataLog
from flet.matplotlib_chart import MatplotlibChart
from datetime import datetime
matplotlib.use("svg")


class TrendViewChart(ft.Container):
    def __init__(self):
        super().__init__()

        self.expand = True
        self.chart = None
        self.ax_rpm = None
        self.ax_power = None

    def update_chart(self, data_list: list[DataLog]):
        date_times, rpm_data, power_data = self.__get_data(data_list)
        self.ax_rpm.plot(date_times, rpm_data, color='red')
        self.ax_power.plot(date_times, power_data, color='blue')
        self.chart.update()

    def __get_data(self, data_list: list[DataLog]):
        date_times = []
        rpm_data = []
        power_data = []

        for data in data_list:
            rpm_data.append(data.revolution)
            power_data.append(data.power)
            date_times.append(
                datetime.strptime(
                    f"{data.utc_date} {data.utc_time}", "%Y-%m-%d %H:%M:%S.%f"
                )
            )

        return (date_times, rpm_data, power_data)

    def build(self):
        width = self.page.window.width
        height = self.page.window.height * 0.7
        aspect_ratio = width / height

        fig, self.ax_rpm = plt.subplots(figsize=(aspect_ratio*10, 10))
        fig.subplots_adjust(left=0.08, right=0.92, top=0.95, bottom=0.1)

        self.ax_rpm.set_xlabel('UTC date time', color='#FF6B00', fontsize=20)
        self.ax_rpm.tick_params(axis='x', labelcolor='#FF6B00', labelsize=16)

        # ax1.xaxis.set_major_locator(
        #     plt.matplotlib.dates.SecondLocator(
        #         interval=math.ceil(5))
        # )

        self.ax_rpm.xaxis.set_major_formatter(
            plt.matplotlib.dates.DateFormatter('%y-%m-%d %H:%M')
        )

        self.ax_rpm.set_ylabel('rpm', color='red', fontsize=20)
        self.ax_rpm.plot([], [], color='red')
        self.ax_rpm.tick_params(axis='y', labelcolor='red', labelsize=16)

        # instantiate a second Axes that shares the same x-axis
        self.ax_power = self.ax_rpm.twinx()

        # we already handled the x-label with ax1
        self.ax_power.set_ylabel('kW', color='blue', fontsize=20)
        self.ax_power.plot([], [], color='blue')
        self.ax_power.tick_params(axis='y', labelcolor='blue', labelsize=16)

        self.chart = MatplotlibChart(
            fig, isolated=True, transparent=True, expand=True)
        self.content = self.chart
