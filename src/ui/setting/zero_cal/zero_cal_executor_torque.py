import asyncio
import logging
import flet as ft
from common.global_data import gdata
from jm3846.JM3846_calculator import JM3846Calculator
from jm3846.JM3846_torque_rpm_util import JM3846TorqueRpmUtil


class ZeroCalExecutorTorque(ft.Card):
    def __init__(self, name: str, on_finish_callback: callable, on_abort_callback: callable):
        super().__init__()
        self.name = name
        self.expand = True
        self.height = 300
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.index = 0
        self.countdown_task = None

        self.sum_torque_offset = 0
        self.on_finish = on_finish_callback
        self.on_abort_callback = on_abort_callback

    def build(self):
        try:
            s = self.page.session
            title = ft.Text(
                value=s.get("lang.zero_cal.mv_per_v_for_torque"),
                size=14,
                weight=ft.FontWeight.W_500
            )

            self.title_container = ft.Container(
                padding=ft.padding.only(top=10),
                content=title
            )

            self.fetch_button = ft.FilledButton(
                text=self.page.session.get("lang.zero_cal.fetch_data"),
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE, width=100, on_click=self.on_fetch
            )

            self.abort_button = ft.FilledButton(
                text=self.page.session.get("lang.zero_cal.abort"),
                bgcolor=ft.Colors.RED, visible=False,
                color=ft.Colors.WHITE, width=100, on_click=lambda e: self.on_abort()
            )

            show_thrust = gdata.configCommon.show_thrust
            self.items = ft.GridView(
                padding=ft.padding.all(10),
                expand=True,
                runs_count=3 if show_thrust else 6,  # 每行3个子元素
                child_aspect_ratio=1.8 if show_thrust else 1,
                spacing=10,  # 子元素间距
                run_spacing=10,
                controls=[ft.Container(
                    content=ft.Text('', size=24),
                    alignment=ft.alignment.center,
                    border=ft.border.all(.5, ft.Colors.ON_SURFACE),
                    border_radius=10,
                ) for i in range(0, 6)]
            )

            self.operation = ft.Container(
                height=60,
                padding=ft.padding.only(bottom=10),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        self.fetch_button,
                        self.abort_button
                    ]
                ))

            self.content = ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                run_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    self.title_container,
                    self.items,
                    self.operation
                ]
            )

        except:
            logging.exception('exception occured at ZeroCalExecutor.build')

    def on_fetch(self, e):
        # 开始采集thrust-ad1
        if self.name == 'sps':
            gdata.configSPS.zero_cal_torque_running = True
        else:
            gdata.configSPS2.zero_cal_torque_running = True

        self.countdown_task = self.page.run_task(self.handle_countdown)

    async def handle_countdown(self):
        try:
            # 点击后隐藏fetch按钮
            if self.fetch_button and self.fetch_button.page:
                self.fetch_button.disabled = True
                self.fetch_button.update()

            countdown_seconds = 2
            while countdown_seconds > 0:
                self.set_mv_per_v(self.index, f'{countdown_seconds}s')
                await asyncio.sleep(1)
                countdown_seconds -= 1

            # 2s倒计时结束，开始统计thrust-ad1
            data_list = gdata.configSPS.zero_cal_ad0_for_torque if self.name == 'sps' else gdata.configSPS2.zero_cal_ad0_for_torque
            gain_0 = gdata.configSPS.gain_0 if self.name == 'sps' else gdata.configSPS2.gain_0
            result = JM3846TorqueRpmUtil.get_avg(data_list, self.name)
            avg_ad0: float = result[0]
            mv_per_v = JM3846Calculator.calculate_mv_per_v(avg_ad0, gain_0)

            # 处理完成清空cache
            if self.name == 'sps':
                gdata.configSPS.zero_cal_ad0_for_torque.clear()
            elif self.name == 'sps2':
                gdata.configSPS2.zero_cal_ad0_for_torque.clear()

            self.set_mv_per_v(self.index, round(mv_per_v, 4))
            self.sum_torque_offset += mv_per_v

            self.index += 1
            # 如果全部采集完成，并且完成回调函数不为空，触发回调完成
            if self.index >= 6 and self.on_finish:
                self.countdown_task.cancel()
                self.on_finish(round(self.sum_torque_offset / 6, 4))

        except:
            logging.exception('exception occured at ZeroCalExecutorTorque.handle_countdown')
        finally:
            # 只需要做6次
            # 如果不够6次，fetch_button按钮是一定需要看到的
            if self.fetch_button and self.fetch_button.page:
                self.fetch_button.disabled = self.index >= 6
                self.fetch_button.update()

            # 取消按钮，只要大于1次就需要被看到
            if self.abort_button and self.abort_button.page:
                self.abort_button.visible = self.index > 0
                self.abort_button.update()

            # 大于6次，次数恢复成0
            self.index = 0 if self.index > 6 else self.index

            # 倒计时执行完毕
            if self.name == 'sps':
                gdata.configSPS.zero_cal_torque_running = False
            else:
                gdata.configSPS2.zero_cal_torque_running = False

    def set_mv_per_v(self, index, value):
        if self.items and self.items.page:
            container: ft.Container = self.items.controls[index]
            txt: ft.Text = container.content

            if txt and txt.page:
                txt.value = value
                txt.update()

    def on_abort(self):
        try:
            if self.fetch_button and self.fetch_button.page:
                self.fetch_button.disabled = False
                self.fetch_button.update()

            for idx in range(0, 6, 1):
                self.set_mv_per_v(idx, '')

            if self.countdown_task:
                self.countdown_task.cancel()
            self.index = 0
            if self.on_abort_callback:
                self.on_abort_callback()
        except:
            logging.exception('exception occured at ZeroCalExecutor.on_abort')

    def reset(self):
        self.on_abort()

    def will_unmount(self):
        if self.countdown_task:
            self.countdown_task.cancel()
