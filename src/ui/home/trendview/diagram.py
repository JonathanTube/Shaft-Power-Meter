import flet as ft
from matplotlib import pyplot as plt
import matplotlib
from db.models.data_log import DataLog
from db.models.date_time_conf import DateTimeConf
from flet.matplotlib_chart import MatplotlibChart
from matplotlib import dates as mdates
from db.models.preference import Preference
from utils.unit_converter import UnitConverter
from typing import List
matplotlib.use('Agg')  # 使用非GUI后端


class TrendViewDiagram(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.data_list = []
        self._init_configurations()

    def _init_configurations(self):
        """初始化配置参数"""
        datetime_conf = DateTimeConf.get()
        preference = Preference.get()

        self.date_format = datetime_conf.date_format
        self.system_unit = preference.system_unit

    def build(self):
        self.set_style()
        self.chart = self._create_initial_chart()
        self.content = self.chart

    def _create_initial_chart(self):
        """创建初始图表结构"""
        self.fig, self.ax_rpm = plt.subplots(figsize=(10, 5.5))
        self.fig.subplots_adjust(left=0.08, right=0.92, top=0.95, bottom=0.1)
        self._configure_axes()
        self._setup_power_axis()
        self.handle_update_chart()
        return MatplotlibChart(
            self.fig,
            isolated=True,
            expand=True,
            transparent=True
        )

    def _configure_axes(self):
        """配置主轴参数"""
        # 日期轴格式化
        self.ax_rpm.xaxis.set_major_locator(mdates.AutoDateLocator())
        self.ax_rpm.xaxis.set_major_formatter(
            mdates.ConciseDateFormatter(self.ax_rpm.xaxis.get_major_locator())
        )

        # 主轴样式
        self.ax_rpm.set_xlabel(xlabel=self.page.session.get('lang.common.utc_date_time'), fontsize=10)
        self.ax_rpm.set_ylabel(ylabel="RPM", fontsize=10)
        self.ax_rpm.grid(True, linestyle=':', alpha=0.5)
        self.ax_rpm.tick_params(axis='both', which='major', labelsize=8)

    def _setup_power_axis(self):
        """配置功率副轴"""
        self.ax_power = self.ax_rpm.twinx()
        unit_label = 'kW' if self.system_unit == 0 else 'sHp'
        self.ax_power.set_ylabel(unit_label, fontsize=10)
        self.ax_power.tick_params(axis='y', labelsize=8)

        # 设置双轴图例
        self._create_legends()

    def _create_legends(self):
        """创建组合图例"""
        lines = [
            self.ax_rpm.plot([], [], label=self.page.session.get('lang.common.speed'), color='blue')[0],
            self.ax_power.plot([], [], label=self.page.session.get('lang.common.power'), color='red')[0]
        ]
        self.ax_rpm.legend(handles=lines, loc='upper left', fontsize=10)

    def update_chart(self, data_list: List[DataLog]):
        self.data_list = data_list
        self.handle_update_chart()

    def handle_update_chart(self):
        """更新图表数据"""
        if not self.data_list:
            return

        # 清除旧数据
        for ax in [self.ax_rpm, self.ax_power]:
            for line in ax.lines:
                line.remove()

        # 获取新数据
        date_times, rpm_data, power_data = self._process_data()

        # 绘制新曲线
        self.ax_rpm.plot(date_times, rpm_data, color='blue')
        self.ax_power.plot(date_times, power_data, color='red')

        # 自动调整范围
        self.ax_rpm.relim()
        self.ax_rpm.autoscale_view()
        self.ax_power.relim()
        self.ax_power.autoscale_view()

        # 更新图表
        self.chart.update()

    def _process_data(self):
        """处理原始数据"""
        date_times = []
        rpm_data = []
        power_data = []

        for data in self.data_list:
            date_times.append(data.utc_date_time)
            rpm_data.append(data.speed)

            if self.system_unit == 0:
                power_data.append(data.power / 1000)
            else:
                power_data.append(UnitConverter.w_to_shp(data.power))

        return date_times, rpm_data, power_data

    def set_style(self):
        # 重新应用样式
        if self.page.theme_mode == ft.ThemeMode.DARK:
            plt.style.use('dark_background')
        else:
            plt.style.use('default')
        """更新主题样式"""
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei',  'WenQuanYi Zen Hei']  # 指定常用中文字体
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题

    def update_style(self):
        self.set_style()
        plt.close(self.fig)
        self.chart = self._create_initial_chart()
        self.content = self.chart
        self.update()
