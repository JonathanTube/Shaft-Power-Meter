import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import flet as ft
from flet.matplotlib_chart import MatplotlibChart
from db.table_init import PropellerSetting
from common.global_data import gdata
import logging

matplotlib.use('Agg')  # 使用非GUI后端
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']  # 指定常用中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题

class PropellerCurveDiagram(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

        ps: PropellerSetting = PropellerSetting.get()

        # MCR点
        self.rpm_of_mcr = ps.rpm_of_mcr_operating_point
        self.power_of_mcr = ps.shaft_power_of_mcr_operating_point

        # 正常螺旋桨曲线
        self.left_rpm_of_normal = ps.rpm_left_of_normal_propeller_curve
        self.left_power_of_normal = ps.bhp_left_of_normal_propeller_curve

        self.right_rpm_of_normal = ps.rpm_right_of_normal_propeller_curve
        self.right_power_of_normal = ps.bhp_right_of_normal_propeller_curve

        self.color_of_normal = ps.line_color_of_normal_propeller_curve

        # 轻载螺旋桨曲线
        self.power_of_light_load = ps.value_of_light_propeller_curve
        self.color_of_light_load = ps.line_color_of_light_propeller_curve

        # 转速限制曲线
        self.rpm_of_speed_limit = ps.value_of_speed_limit_curve
        self.color_of_speed_limit = ps.line_color_of_speed_limit_curve

        # 扭矩/转速限制曲线
        self.left_rpm_of_torque_limit = ps.rpm_left_of_torque_load_limit_curve
        self.left_power_of_torque_limit = ps.bhp_left_of_torque_load_limit_curve
        self.right_rpm_of_torque_limit = ps.rpm_right_of_torque_load_limit_curve
        self.right_power_of_torque_limit = ps.bhp_right_of_torque_load_limit_curve
        self.color_of_torque_limit = ps.line_color_of_torque_load_limit_curve

        # 过载曲线
        self.power_of_overload = ps.value_of_overload_curve
        self.color_of_overload = ps.line_color_of_overload_curve

        self.sps1_point = None
        self.sps2_point = None
        self.sps1_text = None
        self.sps2_text = None

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
        fig, ax = plt.subplots(figsize=(10, 6))
        self.handle_mcr_point(ax)
        self.handle_normal_propeller_curve(ax)
        self.handle_speed_limit(ax)
        self.handle_light_load_propeller_curve(ax)
        self.handle_torque_or_speed_limit_curve(ax)
        self.handle_overload_curve(ax)
        self.handle_style(ax)
        # 优化布局
        fig.tight_layout()
        self.sps1_point = ax.scatter(0, 0, color='orange', zorder=10, label='SPS1 Operating Point', s=40)
        self.sps1_text = ax.text(0, 0, 'SPS1', ha='center', va='bottom', fontsize=8)
        self.sps2_point = ax.scatter(0, 0, color='purple', zorder=10, label='SPS2 Operating Point', s=40)
        self.sps2_text = ax.text(0, 0, 'SPS2', ha='center', va='bottom', fontsize=8)
        return MatplotlibChart(fig, isolated=True, expand=True, transparent=True)

    def handle_style(self, ax):
        # 配置样式
        ax.set_xlabel(self.page.session.get('lang.propeller_curve.engine_speed'), fontsize=10)      
        ax.set_ylabel(self.page.session.get('lang.propeller_curve.engine_shaft_power'), fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.2)
        ax.legend(loc='upper left', fontsize=10)
        # 设置x轴和y轴为对数坐标
        ax.set_xscale('log')
        ax.set_yscale('log')
        self.handle_x_axis(ax)
        self.handle_y_axis(ax)
        # 隐藏上边框和右边框
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    def handle_x_axis(self, ax):
        # 设置x轴刻度
        x_begin = int(self.left_rpm_of_torque_limit // 10)
        x_ticks = [self.left_rpm_of_torque_limit]
        for i in range(x_begin + 1, 12, 1):
            x_ticks.append(i * 10)

        plt.xticks(x_ticks, [f'{x}' for x in x_ticks], fontsize=10)
        # 设置x轴范围
        ax.set_xlim(xmin=x_ticks[0], xmax=x_ticks[-1])

    def handle_y_axis(self, ax):
        # 设置y轴刻度
        y_begin = int(self.left_power_of_normal // 10)
        y_ticks = [self.left_power_of_normal]
        for i in range(y_begin + 1, 12, 1):
            y_ticks.append(i * 10)

        plt.yticks(y_ticks, [f'{x}' for x in y_ticks], fontsize=10)
        # 设置y轴范围
        ax.set_ylim(ymin=y_ticks[0], ymax=y_ticks[-1])

    def handle_mcr_point(self, ax):
        ax.scatter(100, 100, color='red', zorder=5, label=self.page.session.get('lang.propeller_curve.mcr_operating_point'), s=40)

    def handle_normal_propeller_curve(self, ax):
        color = self.color_of_normal
        rpm_points = np.linspace(self.left_rpm_of_normal, 105, 500)
        power_points = (rpm_points / self.right_rpm_of_normal) ** 3 * self.right_power_of_normal
        power_points = np.minimum(power_points, 100)
        ax.plot(rpm_points, power_points, color=color, linewidth=1, label=self.page.session.get('lang.propeller_curve.normal_propeller_curve'))
        ax.scatter([self.left_rpm_of_normal, self.right_rpm_of_normal], [self.left_power_of_normal, self.right_power_of_normal], color=color, zorder=1, s=10)  # 标出两端点

    def handle_speed_limit(self, ax):
        ax.axvline(x=self.rpm_of_speed_limit, color=self.color_of_speed_limit, linewidth=1, label=self.page.session.get('lang.propeller_curve.speed_limit_curve'))

    def handle_light_load_propeller_curve(self, ax):
        color = self.color_of_light_load
        rpm_points = np.linspace(self.left_rpm_of_normal, 105, 500)
        power_points = (rpm_points / self.right_rpm_of_normal) ** 3 * (self.right_power_of_normal + self.power_of_light_load * -1)
        power_points = np.minimum(power_points, 100)
        # power_points = np.maximum(power_points, left_power_of_normal)
        ax.plot(rpm_points, power_points, color=color, linewidth=1, linestyle='dashed', label=self.page.session.get('lang.propeller_curve.light_propeller_curve'))

    def handle_torque_or_speed_limit_curve(self, ax):
        color = self.color_of_torque_limit
        rpm_points = np.linspace(self.left_rpm_of_torque_limit, self.right_rpm_of_torque_limit, 500)
        # add 100 to the end of rpm_points
        rpm_points = np.append(rpm_points, 100)
        power_points = (rpm_points / self.right_rpm_of_torque_limit) ** 2 * self.right_power_of_torque_limit
        power_points = np.minimum(power_points, 100)
        ax.plot(rpm_points, power_points, color=color, linewidth=1, label=self.page.session.get('lang.propeller_curve.torque_load_limit_curve'))
        ax.scatter([self.left_rpm_of_torque_limit, self.right_rpm_of_torque_limit], [self.left_power_of_torque_limit, self.right_power_of_torque_limit], color=color, zorder=2, s=10)  # 标出两端点

    def handle_overload_curve(self, ax):
        color = self.color_of_overload
        rpm_points = np.linspace(self.left_rpm_of_torque_limit, 100, 500)
        power_points = (rpm_points / self.right_rpm_of_torque_limit) ** 2 * (self.right_power_of_torque_limit + self.power_of_overload)
        max_power_point = np.max(power_points)
        rpm_points = np.append(rpm_points, 105)
        power_points = np.append(power_points, max_power_point)
        ax.plot(rpm_points, power_points, color=color, linewidth=1, linestyle='--', label=self.page.session.get('lang.propeller_curve.overload_curve'))

    def update_sps_points(self):
        if self.rpm_of_mcr == 0 or self.power_of_mcr == 0:
            return

        sps1_percent_rpm_of_mcr = round(gdata.sps1_speed / self.rpm_of_mcr * 100, 2)
        sps1_percent_power_of_mcr = round(gdata.sps1_power / self.power_of_mcr * 100, 2)
        self.sps1_point.set_offsets([sps1_percent_rpm_of_mcr, sps1_percent_power_of_mcr])
        self.sps1_text.set_x(sps1_percent_rpm_of_mcr)
        self.sps1_text.set_y(sps1_percent_power_of_mcr + 1)

        sps2_percent_rpm_of_mcr = round(gdata.sps2_speed / self.rpm_of_mcr * 100, 2)
        sps2_percent_power_of_mcr = round(gdata.sps2_power / self.power_of_mcr * 100, 2)
        self.sps2_point.set_offsets([sps2_percent_rpm_of_mcr, sps2_percent_power_of_mcr])
        self.sps2_text.set_x(sps2_percent_rpm_of_mcr)
        self.sps2_text.set_y(sps2_percent_power_of_mcr + 1)

        logging.info(f'update_sps1_points: sps1_percent_rpm_of_mcr={sps1_percent_rpm_of_mcr}%, sps1_percent_power_of_mcr={sps1_percent_power_of_mcr}%')
        logging.info(f'update_sps2_points: sps2_percent_rpm_of_mcr={sps2_percent_rpm_of_mcr}%, sps2_percent_power_of_mcr={sps2_percent_power_of_mcr}%')

        self.chart.update()
