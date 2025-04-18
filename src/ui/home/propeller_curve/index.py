import asyncio
import flet as ft

from db.models.propeller_setting import PropellerSetting
from db.models.system_settings import SystemSettings
from ui.home.propeller_curve.propeller_curve_chart import PropellerCurveChart
from ui.home.propeller_curve.propeller_curve_legend import PropellerCurveLegend
from common.global_data import gdata


class PropellerCurve(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 20

        self.__load_config()

    def build(self):
        self.chart = PropellerCurveChart()
        self.legend = PropellerCurveLegend(
            normal_propeller_color=self.propeller_setting.line_color_of_normal_propeller_curve,
            light_propeller_color=self.propeller_setting.line_color_of_light_propeller_curve,
            speed_limit_color=self.propeller_setting.line_color_of_speed_limit_curve,
            torque_load_limit_color=self.propeller_setting.line_color_of_torque_load_limit_curve,
            overload_color=self.propeller_setting.line_color_of_overload_curve
        )
        self.content = ft.Stack(
            alignment=ft.alignment.center,
            controls=[
                self.legend,
                self.chart
            ])

    def __load_config(self):
        self.propeller_setting = PropellerSetting.get()
        self.system_setting = SystemSettings.get()

    async def __load_data(self):
        if self.propeller_setting.shaft_power_of_mcr_operating_point == 0:
            return
        if self.propeller_setting.rpm_of_mcr_operating_point == 0:
            return

        while True:
            sps1_instant_power = gdata.sps1_power
            sps1_instant_speed = gdata.sps1_speed

            sps1_speed = (
                sps1_instant_speed / self.propeller_setting.rpm_of_mcr_operating_point
            ) * 100

            sps1_power = (
                sps1_instant_power /
                self.propeller_setting.shaft_power_of_mcr_operating_point
            ) * 100

            # print('sps1_speed=', sps1_speed)
            # print('sps1_power=', sps1_power)

            self.chart.update_dynamic_data_sps1(sps1_speed, sps1_power)

            if self.system_setting.amount_of_propeller == 2:
                sps2_speed = (
                    gdata.sps2_speed / self.propeller_setting.rpm_of_mcr_operating_point
                ) * 100

                sps2_power = (
                    gdata.sps2_power / self.propeller_setting.shaft_power_of_mcr_operating_point
                ) * 100

                self.chart.update_dynamic_data_sps2(sps2_speed, sps2_power)

            await asyncio.sleep(1)

    def did_mount(self):
        self.chart.update_static_data(
            normal_rpm_left=self.propeller_setting.rpm_left_of_normal_propeller_curve,
            normal_power_left=self.propeller_setting.bhp_left_of_normal_propeller_curve,
            normal_rpm_right=self.propeller_setting.rpm_right_of_normal_propeller_curve,
            normal_power_right=self.propeller_setting.bhp_right_of_normal_propeller_curve,
            normal_line_color=self.propeller_setting.line_color_of_normal_propeller_curve,

            light_propeller=self.propeller_setting.value_of_light_propeller_curve,
            light_propeller_line_color=self.propeller_setting.line_color_of_light_propeller_curve,

            speed_limit=self.propeller_setting.value_of_speed_limit_curve,
            speed_limit_line_color=self.propeller_setting.line_color_of_speed_limit_curve,

            torque_load_limit_rpm_left=self.propeller_setting.rpm_left_of_torque_load_limit_curve,
            torque_load_limit_power_left=self.propeller_setting.bhp_left_of_torque_load_limit_curve,
            torque_load_limit_rpm_right=self.propeller_setting.rpm_right_of_torque_load_limit_curve,
            torque_load_limit_power_right=self.propeller_setting.bhp_right_of_torque_load_limit_curve,
            torque_load_limit_line_color=self.propeller_setting.line_color_of_torque_load_limit_curve,

            overload=self.propeller_setting.value_of_overload_curve,
            overload_line_color=self.propeller_setting.line_color_of_overload_curve
        )

        self._task = self.page.run_task(self.__load_data)

    def will_unmount(self):
        self._task.cancel()
