import logging
import flet as ft
import matplotlib.backends.backend_svg
from matplotlib import pyplot as plt
from db.models.data_log import DataLog
from flet.matplotlib_chart import MatplotlibChart
from matplotlib import dates as mdates
from utils.unit_converter import UnitConverter
from typing import List
from common.global_data import gdata

matplotlib.use('Agg')  # 使用非GUI后端
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']  # 指定常用中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题


class TrendViewDiagram(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.data_list = []
        self.system_unit = gdata.configPreference.system_unit
        self.fig = None
        self.ax_rpm = None
        self.ax_power = None
        self.chart = None

    def did_mount(self):
        # Ensure chart is created when control is mounted
        self.before_update()

    def before_update(self):
        try:
            # 清除当前图形缓存
            plt.close('all')
            # 重新应用样式
            self.set_style()
            # 重建图表对象
            self.chart = self.create_chart()
            if self.chart:
                # 替换容器内容
                self.content = self.chart
        except:
            logging.exception('exception occured at TrendViewDiagram.before_update')

    def create_chart(self) -> MatplotlibChart:
        try:
            self.set_style()
            """创建初始图表结构"""
            self.fig, self.ax_rpm = plt.subplots(figsize=(10, 6))
            # self.fig.subplots_adjust(left=0.08, right=0.92, top=0.98, bottom=0.1)
            self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.01)
            self.fig.autofmt_xdate()
            self._configure_axes()
            self._setup_power_axis()
            self.handle_update_chart()
            return MatplotlibChart(self.fig, isolated=True, expand=True, transparent=True)
        except:
            logging.exception("exception occured at TrendViewDiagram.create_chart")
            return None

    def set_style(self):
        # 重新应用样式
        if self.page and self.page.theme_mode == ft.ThemeMode.DARK:
            plt.style.use('dark_background')
        else:
            plt.style.use('default')
        """更新主题样式"""
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei',  'WenQuanYi Zen Hei']  # 指定常用中文字体
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题

    def _configure_axes(self):
        """配置主轴参数"""
        if not self.ax_rpm:
            return
        # self.ax_rpm.xaxis.set_major_locator(mdates.HourLocator(byhour=range(0, 24, 2)))
        # self.ax_rpm.xaxis.set_major_formatter(mdates.DateFormatter(f'%H:%M'))

        # 主轴样式
        # if self.page and self.page.session:
        #     self.ax_rpm.set_xlabel(xlabel=self.page.session.get('lang.common.utc_date_time'), fontsize=10)

        self.ax_rpm.set_xticks([])      # 不显示刻度
        self.ax_rpm.set_xticklabels([]) # 不显示刻度文字
        self.ax_rpm.set_xlabel("")      # 不显示 X 轴标签

        self.ax_rpm.set_ylabel(ylabel="RPM", fontsize=10)
        self.ax_rpm.grid(True, linestyle=':', alpha=0.5)
        self.ax_rpm.tick_params(axis='both', which='major', labelsize=8)

    def _setup_power_axis(self):
        """配置功率副轴"""
        if not self.ax_rpm:
            return
        self.ax_power = self.ax_rpm.twinx()
        unit_label = 'kW' if self.system_unit == 0 else 'sHp'
        self.ax_power.set_ylabel(unit_label, fontsize=10)
        self.ax_power.tick_params(axis='y', labelsize=8)

        # 设置双轴图例
        self._create_legends()

    def _create_legends(self):
        """创建组合图例"""
        if not self.ax_rpm or not self.ax_power:
            return
        if self.page and self.page.session:
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
        if not self.data_list or not self.ax_rpm or not self.ax_power:
            return

        # 清除旧数据
        for ax in [self.ax_rpm, self.ax_power]:
            # copy list to avoid iteration issues while removing
            for line in list(ax.lines):
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

    def will_unmount(self):
        plt.close('all')
