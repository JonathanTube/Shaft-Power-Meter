import flet as ft
from matplotlib import pyplot as plt
import matplotlib
from db.models.data_log import DataLog
from db.models.date_time_conf import DateTimeConf
from flet.matplotlib_chart import MatplotlibChart

matplotlib.use('Agg')  # 使用非GUI后端


class TrendViewDiagram(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.chart = None
        self.ax_rpm = None
        self.ax_power = None
        datetime_conf: DateTimeConf = DateTimeConf.get()
        self.date_format = datetime_conf.date_format

    def update_chart(self, data_list: list[DataLog]):
        date_times, rpm_data, power_data = self.__get_data(data_list)
        self.ax_rpm.plot(date_times, rpm_data)
        self.ax_power.plot(date_times, power_data)

        self.chart.update()

    def __get_data(self, data_list: list[DataLog]):
        date_times = []
        rpm_data = []
        power_data = []

        for data in data_list:
            rpm_data.append(data.speed)
            power_data.append(data.power)
            date_times.append(data.utc_date_time.strftime(f'{self.date_format} %H:%M:%S'))

        return (date_times, rpm_data, power_data)

    def build(self):
        self.chart = self.create_chart()
        self.content = self.chart

    def update_style(self):
        # 清除当前图形缓存
        plt.close('all')
        # 重新应用样式
        if self.page.theme_mode == ft.ThemeMode.DARK:
            plt.style.use('dark_background')
        else:
            plt.style.use('default')
        # 重建图表对象
        self.chart = self.create_chart()
        # 替换容器内容
        self.content = self.chart
        self.update()

    def create_chart(self) -> MatplotlibChart:
        if self.page.theme_mode == ft.ThemeMode.DARK:
            plt.style.use('dark_background')
        else:
            plt.style.use('default')
        fig, self.ax_rpm = plt.subplots(figsize=(10, 6))
        fig.subplots_adjust(left=0.08, right=0.92, top=0.95, bottom=0.1)

        self.ax_rpm.grid(True, linestyle='--', alpha=0.2)
        self.ax_rpm.set_xlabel('UTC date time',  fontsize=12)
        self.ax_rpm.tick_params(axis='x', labelsize=10)

        self.ax_rpm.set_ylabel('rpm',  fontsize=12)
        self.ax_rpm.plot([], [])
        self.ax_rpm.tick_params(axis='y', labelsize=10)
        self.ax_rpm.spines['top'].set_visible(False)

        # instantiate a second Axes that shares the same x-axis
        self.ax_power = self.ax_rpm.twinx()

        # we already handled the x-label with ax1
        self.ax_power.set_ylabel('kW', fontsize=10)
        self.ax_power.plot([], [])
        self.ax_power.tick_params(axis='y', labelsize=10)
        self.ax_power.spines['top'].set_visible(False)

        # 优化布局
        fig.tight_layout()

        return MatplotlibChart(fig, isolated=True, expand=True, transparent=True)
