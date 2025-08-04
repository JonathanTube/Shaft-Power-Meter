import logging
import flet as ft
from db.models.zero_cal_info import ZeroCalInfo
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
        self.torque_offset = None
        self.thrust_offset = None

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
                on_click=self.on_accept
            )

            self.content = ft.Column(
                spacing=0,
                controls=[
                    self.zeroCalExecutorTips,
                    ft.Row(
                        spacing=0,
                        controls=[
                            self.zeroCalExecutorTorque,
                            self.zeroCalExecutorThrust
                        ]
                    ),
                    self.zeroCalExecutorResult,
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            self.accept_button
                        ])
                ])
        except:
            logging.exception('exception occured at ZeroCalExecutor.build')

    def on_torque_finish(self, avg_torque):
        self.torque_offset = avg_torque
        self.update_buttons()
        self.update_result()

    def on_thrust_finish(self, avg_thrust):
        self.thrust_offset = avg_thrust
        self.update_buttons()
        self.update_result()

    def on_torque_abort(self):
        self.torque_offset = None
        self.update_buttons()
        self.update_result()

    def on_thrust_abort(self):
        self.thrust_offset = None
        self.update_buttons()
        self.update_result()

    def is_all_finish(self):
        return self.torque_offset is not None and self.thrust_offset is not None

    def update_buttons(self):
        finished = self.is_all_finish()
        if self.accept_button and self.accept_button.page:
            self.accept_button.visible = finished
            self.accept_button.page.update()

    def update_result(self):
        if not self.is_all_finish():
            return

        last_record = self.load_last_accepted_zero_cal()
        last_torque_offset = 0
        if last_record:
            last_torque_offset = last_record.torque_offset

        # 这里当前的平均值 - 上一次的，不就相当于每次减一下，除以6，和一下等式作用一样
        self.torque_offset = self.torque_offset - last_torque_offset

        self.zeroCalExecutorResult.update_result(
            self.torque_offset, self.thrust_offset
        )

    def on_accept(self, e):
        try:
            ZeroCalInfo.create(
                utc_date_time=gdata.utc_date_time, name=self.name,
                torque_offset=self.torque_offset, thrust_offset=self.thrust_offset
            )

            # 设置全局变量
            if self.name == 'sps':
                gdata.sps_torque_offset = self.torque_offset
                gdata.sps_thrust_offset = self.thrust_offset
            else:
                gdata.sps2_torque_offset = self.torque_offset
                gdata.sps2_thrust_offset = self.thrust_offset

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
