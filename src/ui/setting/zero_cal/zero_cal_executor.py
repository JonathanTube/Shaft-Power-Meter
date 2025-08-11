import logging
import flet as ft
from db.models.system_settings import SystemSettings
from db.models.zero_cal_info import ZeroCalInfo
from ui.common.permission_check import PermissionCheck
from ui.setting.zero_cal.zero_cal_executor_result import ZeroCalExecutorResult
from ui.setting.zero_cal.zero_cal_executor_thrust import ZeroCalExecutorThrust
from ui.setting.zero_cal.zero_cal_executor_tips import ZeroCalExecutorTips
from ui.setting.zero_cal.zero_cal_executor_torque import ZeroCalExecutorTorque
from common.global_data import gdata
from ui.common.toast import Toast


class ZeroCalExecutor(ft.Container):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

        self.is_torque_finish = False
        self.is_thrust_finish = False
        self.torque_offset = 0
        self.thrust_offset = 0

        system_settings: SystemSettings = SystemSettings.get()
        self.display_thrust = system_settings.display_thrust

    def build(self):
        try:
            self.zeroCalExecutorTips = ZeroCalExecutorTips(self.name)
            self.zeroCalExecutorTorque = ZeroCalExecutorTorque(
                self.name, on_finish_callback=self.on_torque_finish, on_abort_callback=self.on_torque_abort
            )
            self.zeroCalExecutorThrust = ZeroCalExecutorThrust(
                self.name, on_finish_callback=self.on_thrust_finish, on_abort_callback=self.on_thrust_abort
            )
            self.zeroCalExecutorResult = ZeroCalExecutorResult(self.name)

            self.accept_button = ft.FilledButton(
                text=self.page.session.get("lang.zero_cal.accept"),
                bgcolor=ft.Colors.LIGHT_GREEN, color=ft.Colors.WHITE,
                width=120, height=40, visible=False,
                on_click=lambda e: self.page.open(PermissionCheck(self.on_accept, 0))
            )

            controls = [
                self.zeroCalExecutorTorque
            ]

            if self.display_thrust:
                controls.append(self.zeroCalExecutorThrust)

            self.content = ft.Column(
                spacing=0,
                controls=[
                    self.zeroCalExecutorTips,
                    ft.Row(
                        spacing=0,
                        controls=controls
                    ),
                    self.zeroCalExecutorResult,
                    ft.Container(width=100, height=10),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            self.accept_button
                        ])
                ])
        except:
            logging.exception('exception occured at ZeroCalExecutor.build')

    def on_torque_finish(self, avg_torque):
        self.is_torque_finish = True
        self.torque_offset = avg_torque
        self.update_buttons()
        # 获取最后一次
        last_record = self.load_last_accepted_zero_cal()
        last_torque_offset = last_record.torque_offset if last_record else 0
        # 这里当前的平均值 - 上一次的，不就相当于每次减一下，除以6，和一下等式作用一样
        self.torque_offset = round(self.torque_offset - last_torque_offset, 4)
        self.zeroCalExecutorResult.update_torque_result(self.torque_offset)

    def on_torque_abort(self):
        self.is_torque_finish = False
        self.torque_offset = 0
        self.update_buttons()
        self.zeroCalExecutorResult.update_torque_result(0)

    def on_thrust_finish(self, avg_thrust):
        self.is_thrust_finish = True
        self.thrust_offset = round(avg_thrust, 4)
        self.update_buttons()
        self.zeroCalExecutorResult.update_thrust_result(self.thrust_offset)

    def on_thrust_abort(self):
        self.is_thrust_finish = False
        self.thrust_offset = 0
        self.update_buttons()
        self.zeroCalExecutorResult.update_thrust_result(0)

    def is_all_finish(self):
        # 如果没有推力，不需要调零
        if self.display_thrust:
            return self.is_torque_finish and self.is_thrust_finish
        return self.is_torque_finish

    def update_buttons(self):
        finished = self.is_all_finish()
        if self.accept_button and self.accept_button.page:
            self.accept_button.visible = finished
            self.accept_button.page.update()

    def on_accept(self, e):
        try:
            ZeroCalInfo.create(
                utc_date_time=gdata.configDateTime.utc, name=self.name,
                torque_offset=self.torque_offset, thrust_offset=self.thrust_offset
            )

            # 设置全局变量
            if self.name == 'sps':
                gdata.configSPS.torque_offset = self.torque_offset
                gdata.configSPS.thrust_offset = self.thrust_offset
            else:
                gdata.configSPS2.sps2_torque_offset = self.torque_offset
                gdata.configSPS2.sps2_thrust_offset = self.thrust_offset

            if self.accept_button and self.accept_button.page:
                self.accept_button.visible = False
                self.accept_button.update()

            self.zeroCalExecutorTips.update()
            self.zeroCalExecutorThrust.reset()
            self.zeroCalExecutorTorque.reset()
            self.zeroCalExecutorResult.update()

            Toast.show_success(self.page)
        except:
            Toast.show_error(self.page)

    def load_last_accepted_zero_cal(self):
        last_accepted_zero_cal: ZeroCalInfo = ZeroCalInfo.select().where(
            ZeroCalInfo.name == self.name
        ).order_by(
            ZeroCalInfo.id.desc()
        ).first()
        return last_accepted_zero_cal
