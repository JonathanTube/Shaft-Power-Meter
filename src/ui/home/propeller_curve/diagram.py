import asyncio
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import flet as ft
from flet.matplotlib_chart import MatplotlibChart
from db.table_init import PropellerSetting
from common.global_data import gdata
import logging

# 使用无 GUI 后端 + 中文字体
matplotlib.use("Agg")
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "WenQuanYi Zen Hei"]
plt.rcParams["axes.unicode_minus"] = False


class PropellerCurveDiagram(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.task_running = False
        self.task = None
        self.chart = None

        ps: PropellerSetting = PropellerSetting.get()

        # 各种曲线参数
        self.rpm_of_mcr = ps.rpm_of_mcr_operating_point
        self.power_of_mcr = ps.shaft_power_of_mcr_operating_point

        self.left_rpm_of_normal = ps.rpm_left_of_normal_propeller_curve
        self.left_power_of_normal = ps.bhp_left_of_normal_propeller_curve
        self.right_rpm_of_normal = ps.rpm_right_of_normal_propeller_curve
        self.right_power_of_normal = ps.bhp_right_of_normal_propeller_curve
        self.color_of_normal = ps.line_color_of_normal_propeller_curve

        self.power_of_light_load = ps.value_of_light_propeller_curve
        self.color_of_light_load = ps.line_color_of_light_propeller_curve

        self.rpm_of_speed_limit = ps.value_of_speed_limit_curve
        self.color_of_speed_limit = ps.line_color_of_speed_limit_curve

        self.left_rpm_of_torque_limit = ps.rpm_left_of_torque_load_limit_curve
        self.left_power_of_torque_limit = ps.bhp_left_of_torque_load_limit_curve
        self.right_rpm_of_torque_limit = ps.rpm_right_of_torque_load_limit_curve
        self.right_power_of_torque_limit = ps.bhp_right_of_torque_load_limit_curve
        self.color_of_torque_limit = ps.line_color_of_torque_load_limit_curve

        self.power_of_overload = ps.value_of_overload_curve
        self.color_of_overload = ps.line_color_of_overload_curve

        # 动态点
        self.sps_point = self.sps2_point = None
        self.sps_text = self.sps2_text = None

    def before_update(self):
        """更新前清理旧图表"""
        if self.chart and hasattr(self.chart, "figure"):
            plt.close(self.chart.figure)

        self.sps_offset_text = ft.Text(value="")
        self.sps2_offset_text = ft.Text(value="")

        self.chart = self.create_chart()
        if self.chart:
            self.content = ft.Column(
                expand=True,
                controls=[
                    ft.Row(controls=[self.sps_offset_text, self.sps2_offset_text], spacing=10),
                    self.chart
                ]
            )

    def set_style(self):
        """主题样式"""
        plt.style.use("dark_background" if self.page.theme_mode == ft.ThemeMode.DARK else "default")

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

            # 动态点
            self.sps_point = ax.scatter(0, 0, color="orange", zorder=10, label="SPS", s=40)
            self.sps_text = ax.text(0, 0, "SPS", ha="center", va="bottom", fontsize=8)
            self.sps2_point = ax.scatter(0, 0, color="purple", zorder=10, label="SPS2", s=40)
            self.sps2_text = ax.text(0, 0, "SPS2", ha="center", va="bottom", fontsize=8)

            return MatplotlibChart(fig, isolated=True, expand=True, transparent=True)
        except:
            logging.exception("PropellerCurveDiagram.create_chart")
            return None

    # ========== 样式 & 坐标轴 ==========
    def handle_style(self, ax):
        ax.set_xlabel(self.page.session.get("lang.propeller_curve.engine_speed"), fontsize=10)
        ax.set_ylabel(self.page.session.get("lang.propeller_curve.engine_shaft_power"), fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.2)
        ax.legend(loc="upper left", fontsize=10)
        self.handle_x_axis(ax)
        self.handle_y_axis(ax)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.subplots_adjust(left=0.1, right=0.95, top=0.98, bottom=0.08)

    def get_left_rpm_point(self): return 5 * math.floor(min(self.left_rpm_of_normal, self.left_rpm_of_torque_limit) / 5)
    def get_left_power_point(self): return 5 * math.floor(min(self.left_power_of_normal, self.left_power_of_torque_limit) / 5)

    def handle_x_axis(self, ax):
        x_begin = self.get_left_rpm_point()
        x_ticks = list(range(x_begin, 115, 5))
        ax.set_xticks(x_ticks)
        ax.set_xlim(x_ticks[0], x_ticks[-1])

    def handle_y_axis(self, ax):
        y_begin = self.get_left_power_point()
        y_ticks = list(range(y_begin, 115, 5))
        ax.set_yticks(y_ticks)
        ax.set_ylim(y_ticks[0], y_ticks[-1])

    # ========== 各种曲线 ==========
    def handle_mcr_point(self, ax):
        ax.scatter(100, 100, color="red", zorder=5,
                   label=self.page.session.get("lang.propeller_curve.mcr_operating_point"), s=40)

    def handle_normal_propeller_curve(self, ax):
        rpm = np.linspace(self.get_left_rpm_point(), 105, 500)
        power = np.minimum((rpm / self.right_rpm_of_normal) ** 3 * self.right_power_of_normal, 100)
        ax.plot(rpm, power, color=self.color_of_normal, linewidth=1,
                label=self.page.session.get("lang.propeller_curve.normal_propeller_curve"))

    def handle_speed_limit(self, ax):
        ax.axvline(x=self.rpm_of_speed_limit, color=self.color_of_speed_limit, linewidth=1,
                   label=self.page.session.get("lang.propeller_curve.speed_limit_curve"))

    def handle_light_load_propeller_curve(self, ax):
        rpm = np.linspace(self.get_left_rpm_point(), 105, 500)
        power = np.minimum((rpm / self.right_rpm_of_normal) ** 3 * (self.right_power_of_normal - self.power_of_light_load), 100)
        ax.plot(rpm, power, color=self.color_of_light_load, linewidth=1, linestyle="dashed",
                label=self.page.session.get("lang.propeller_curve.light_propeller_curve"))

    def handle_torque_or_speed_limit_curve(self, ax):
        rpm = np.linspace(self.get_left_rpm_point(), self.right_rpm_of_torque_limit, 500)
        rpm = np.append(rpm, 100)
        power = np.minimum((rpm / self.right_rpm_of_torque_limit) ** 2 * self.right_power_of_torque_limit, 100)
        ax.plot(rpm, power, color=self.color_of_torque_limit, linewidth=1,
                label=self.page.session.get("lang.propeller_curve.torque_load_limit_curve"))

    def handle_overload_curve(self, ax):
        rpm = np.linspace(self.get_left_rpm_point(), 100, 500)
        power = (rpm / self.right_rpm_of_torque_limit) ** 2 * (self.right_power_of_torque_limit + self.power_of_overload)
        rpm = np.append(rpm, 105)
        power = np.append(power, np.max(power))
        ax.plot(rpm, power, color=self.color_of_overload, linewidth=1, linestyle="--",
                label=self.page.session.get("lang.propeller_curve.overload_curve"))

    # ========== 动态更新 ==========
    async def update_sps_points(self):
        while self.task_running:
            try:
                if self.rpm_of_mcr and self.power_of_mcr:
                    # SPS
                    x1, y1 = gdata.configSPS.speed / self.rpm_of_mcr * 100, gdata.configSPS.power / self.power_of_mcr * 100

                    if self.sps_offset_text:
                        self.sps_offset_text.value = f"sps.x={round(x1, 1)}%,sps.y={round(y1, 1)}%"
                        self.sps_offset_text.update()

                    if self.sps_point:
                        self.sps_point.set_offsets([x1, y1])
                        self.sps_text.set_position((x1, y1 + 1))
                    # SPS2
                    x2, y2 = gdata.configSPS2.speed / self.rpm_of_mcr * 100, gdata.configSPS2.power / self.power_of_mcr * 100

                    if self.sps2_offset_text:
                        self.sps_offset_text.value = f"sps2.x={round(x2, 1)}%,sps2.y={round(y2, 1)}%"
                        self.sps2_offset_text.update()

                    if self.sps2_point:
                        self.sps2_point.set_offsets([x2, y2])
                        self.sps2_text.set_position((x2, y2 + 1))
                    if self.chart:
                        self.chart.update()
            except:
                logging.exception("update_sps_points")
            await asyncio.sleep(gdata.configPreference.data_collection_seconds_range)

    # ========== 生命周期 ==========
    def did_mount(self):
        self.task_running = True
        self.task = self.page.run_task(self.update_sps_points)

    def will_unmount(self):
        if self.chart and hasattr(self.chart, "figure"):
            plt.close(self.chart.figure)
        self.chart = None
        self.task_running = False
        if self.task:
            self.task.cancel()
