import asyncio
import math
import matplotlib.backends.backend_svg
import matplotlib.pyplot as plt
import numpy as np
import flet as ft
from flet.matplotlib_chart import MatplotlibChart
from db.models.preference import Preference
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

        self.task_running = False

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

        self.sps_point = None
        self.sps2_point = None
        self.sps_text = None
        self.sps2_text = None

    def before_update(self):
        try:
            #  清除当前图形缓存
            plt.close('all')
            # 重新应用样式
            self.set_style()
            # 重建图表对象
            self.chart = self.create_chart()
            if self.chart:
                # 替换容器内容
                self.content = self.chart
        except:
            logging.exception('exception occured at PropellerCurveDiagram.before_update') 

    def create_chart(self) -> MatplotlibChart:
        try:
            self.set_style()
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
            self.sps_point = ax.scatter(0, 0, color='orange', zorder=10, label='SPS Operating Point', s=40)
            self.sps_text = ax.text(0, 0, 'SPS', ha='center', va='bottom', fontsize=8)
            self.sps2_point = ax.scatter(0, 0, color='purple', zorder=10, label='SPS2 Operating Point', s=40)
            self.sps2_text = ax.text(0, 0, 'SPS2', ha='center', va='bottom', fontsize=8)
            return MatplotlibChart(fig, isolated=True, expand=True, transparent=True)
        except:
            logging.exception("exception occured at PropellerCurveDiagram.create_chart")
            return None

    def set_style(self):
        # 重新应用样式
        if self.page.theme_mode == ft.ThemeMode.DARK:
            plt.style.use('dark_background')
        else:
            plt.style.use('default')
        """更新主题样式"""
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei',  'WenQuanYi Zen Hei']  # 指定常用中文字体
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题

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

    def get_left_rpm_point(self):
        rpm_point = min(self.left_rpm_of_normal, self.left_rpm_of_torque_limit)
        return 5 * math.floor(rpm_point / 5)

    def get_left_power_point(self):
        power_point = min(self.left_power_of_normal, self.left_power_of_torque_limit)
        return 5 * math.floor(power_point / 5)

    def handle_x_axis(self, ax):
        # 设置x轴刻度
        x_begin = self.get_left_rpm_point()
        x_ticks = []
        for i in range(x_begin, 115, 5):
            x_ticks.append(i)

        plt.xticks(x_ticks, [f'{x}' for x in x_ticks], fontsize=10)
        # 设置x轴范围
        ax.set_xlim(xmin=x_ticks[0], xmax=x_ticks[-1])

    def handle_y_axis(self, ax):
        # 设置y轴刻度
        y_begin = self.get_left_power_point()
        y_ticks = []
        for i in range(y_begin, 115, 5):
            y_ticks.append(i)

        plt.yticks(y_ticks, [f'{x}' for x in y_ticks], fontsize=10)
        # 设置y轴范围
        ax.set_ylim(ymin=y_ticks[0], ymax=y_ticks[-1])

    def handle_mcr_point(self, ax):
        ax.scatter(100, 100, color='red', zorder=5, label=self.page.session.get('lang.propeller_curve.mcr_operating_point'), s=40)

    def handle_normal_propeller_curve(self, ax):
        color = self.color_of_normal
        rpm_points = np.linspace(self.get_left_rpm_point(), 105, 500)
        # calculate power points via right rpm and power.
        power_points = (rpm_points / self.right_rpm_of_normal) ** 3 * self.right_power_of_normal
        # generate more power points.
        power_points = np.minimum(power_points, 100)
        # plot all of the points on the diagram.
        ax.plot(rpm_points, power_points, color=color, linewidth=1, label=self.page.session.get('lang.propeller_curve.normal_propeller_curve'))
        # mark the left point on the diagram, if the configuration of right point is propable, the line will cross through the left point.
        # ax.scatter([self.left_rpm_of_normal, self.right_rpm_of_normal], [self.left_power_of_normal, self.right_power_of_normal], color=color, zorder=1, s=10)  # 标出两端点

    def handle_speed_limit(self, ax):
        ax.axvline(x=self.rpm_of_speed_limit, color=self.color_of_speed_limit, linewidth=1, label=self.page.session.get('lang.propeller_curve.speed_limit_curve'))

    def handle_light_load_propeller_curve(self, ax):
        color = self.color_of_light_load
        rpm_points = np.linspace(self.get_left_rpm_point(), 105, 500)
        power_points = (rpm_points / self.right_rpm_of_normal) ** 3 * (self.right_power_of_normal + self.power_of_light_load * -1)
        power_points = np.minimum(power_points, 100)
        # power_points = np.maximum(power_points, left_power_of_normal)
        ax.plot(rpm_points, power_points, color=color, linewidth=1, linestyle='dashed', label=self.page.session.get('lang.propeller_curve.light_propeller_curve'))

    def handle_torque_or_speed_limit_curve(self, ax):
        color = self.color_of_torque_limit
        rpm_points = np.linspace(self.get_left_rpm_point(), self.right_rpm_of_torque_limit, 500)
        # add 100 to the end of rpm_points
        rpm_points = np.append(rpm_points, 100)
        power_points = (rpm_points / self.right_rpm_of_torque_limit) ** 2 * self.right_power_of_torque_limit
        power_points = np.minimum(power_points, 100)
        ax.plot(rpm_points, power_points, color=color, linewidth=1, label=self.page.session.get('lang.propeller_curve.torque_load_limit_curve'))
        # ax.scatter([self.left_rpm_of_torque_limit, self.right_rpm_of_torque_limit], [self.left_power_of_torque_limit, self.right_power_of_torque_limit], color=color, zorder=2, s=10)  # 标出两端点

    def handle_overload_curve(self, ax):
        color = self.color_of_overload
        rpm_points = np.linspace(self.get_left_rpm_point(), 100, 500)
        power_points = (rpm_points / self.right_rpm_of_torque_limit) ** 2 * (self.right_power_of_torque_limit + self.power_of_overload)
        max_power_point = np.max(power_points)
        rpm_points = np.append(rpm_points, 105)
        power_points = np.append(power_points, max_power_point)
        ax.plot(rpm_points, power_points, color=color, linewidth=1, linestyle='--', label=self.page.session.get('lang.propeller_curve.overload_curve'))

    async def update_sps_points(self):
        preference: Preference = Preference.get()
        interval = preference.data_refresh_interval
        while self.task_running:
            try:
                if self.rpm_of_mcr == 0 or self.power_of_mcr == 0:
                    return

                sps_percent_rpm_of_mcr = round(gdata.configSPS.sps_speed / self.rpm_of_mcr * 100, 2)
                sps_percent_power_of_mcr = round(gdata.configSPS.sps_power / self.power_of_mcr * 100, 2)
                self.sps_point.set_offsets([sps_percent_rpm_of_mcr, sps_percent_power_of_mcr])
                self.sps_text.set_x(sps_percent_rpm_of_mcr)
                self.sps_text.set_y(sps_percent_power_of_mcr + 1)

                sps2_percent_rpm_of_mcr = round(gdata.configSPS2.sps_speed / self.rpm_of_mcr * 100, 2)
                sps2_percent_power_of_mcr = round(gdata.configSPS2.sps_power / self.power_of_mcr * 100, 2)
                self.sps2_point.set_offsets([sps2_percent_rpm_of_mcr, sps2_percent_power_of_mcr])
                self.sps2_text.set_x(sps2_percent_rpm_of_mcr)
                self.sps2_text.set_y(sps2_percent_power_of_mcr + 1)

                # logging.info(f'update_sps_points: sps_percent_rpm_of_mcr={sps_percent_rpm_of_mcr}%, sps_percent_power_of_mcr={sps_percent_power_of_mcr}%')
                # logging.info(f'update_sps2_points: sps2_percent_rpm_of_mcr={sps2_percent_rpm_of_mcr}%, sps2_percent_power_of_mcr={sps2_percent_power_of_mcr}%')
                if self.chart and self.chart.page:
                    self.chart.update()
            except:
                logging.exception("exception occured at update_sps_points")
            finally:
                await asyncio.sleep(interval)

    def did_mount(self):
        self.task_running = True
        self.task = self.page.run_task(self.update_sps_points)

    def will_unmount(self):
        plt.close('all')
        self.task_running = False
        if self.task:
            self.task.cancel()
