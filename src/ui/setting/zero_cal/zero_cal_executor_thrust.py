import asyncio
import logging
import flet as ft
from common.global_data import gdata
from jm3846.JM3846_calculator import JM3846Calculator
from jm3846.JM3846_thrust_util import JM3846ThrustUtil


class ZeroCalExecutorThrust(ft.Card):
    def __init__(self, name: str, on_finish_callback: callable, on_abort_callback: callable):
        super().__init__()
        self.name = name
        self.expand = True
        self.height = 300
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.tick_task = None
        self.on_finish_callback = on_finish_callback
        self.on_abort_callback = on_abort_callback

        self.abort_button = None
        self.fetch_button = None
        self.seconds_tick = None

    def build(self):
        try:
            s = self.page.session
            title = ft.Text(
                value=s.get("lang.zero_cal.mv_per_v_for_thrust"),
                size=14,
                weight=ft.FontWeight.W_500
            )

            title_container = ft.Container(
                padding=ft.padding.only(top=10), content=title
            )

            self.seconds_tick = ft.Text(
                value="", size=30, weight=ft.FontWeight.W_600
            )

            self.seconds_tick_container = ft.Container(
                alignment=ft.alignment.center,
                expand=True,
                content=self.seconds_tick,
                border=ft.border.all(.5, ft.Colors.ON_SURFACE),
                border_radius=10,
                margin=ft.margin.symmetric(20, 80)
            )

            self.fetch_button = ft.FilledButton(
                text=s.get("lang.zero_cal.fetch_data"), bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE, width=100, on_click=self.on_start
            )

            self.abort_button = ft.FilledButton(
                text=self.page.session.get("lang.zero_cal.abort"),
                bgcolor=ft.Colors.RED, visible=False,
                color=ft.Colors.WHITE, width=100, on_click=lambda e: self.on_abort()
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
                    title_container,
                    self.seconds_tick_container,
                    self.operation
                ]
            )
        except:
            logging.exception(
                "exception occured at ZeroCalExecutorThrust.build"
            )

    def on_start(self, e):
        try:
            if self.page:
                self.tick_task = self.page.run_task(self.on_tick)
        except:
            logging.exception(
                "exception occured at ZeroCalExecutorThrust.on_start"
            )

    def on_abort(self):
        try:
            if self.name == 'sps':
                gdata.configSPS.zero_cal_thrust_running = False
                gdata.configSPS.zero_cal_ad1_for_thrust.clear()
            else:
                gdata.configSPS2.zero_cal_thrust_running = False
                gdata.configSPS2.zero_cal_ad1_for_thrust.clear()

            if self.fetch_button and self.fetch_button.page:
                self.fetch_button.visible = True
                self.fetch_button.update()

            if self.abort_button and self.abort_button.page:
                self.abort_button.visible = False
                self.abort_button.update()

            if self.seconds_tick and self.seconds_tick.page:
                self.seconds_tick.value = ''
                self.seconds_tick.update()

            if self.on_abort_callback:
                self.on_abort_callback()

        except:
            logging.exception("exception occured at ZeroCalExecutorThrust.on_abort")

    async def on_tick(self):
        try:
            if self.name == 'sps':
                if gdata.configSPS.zero_cal_thrust_running:
                    return
                # 标记调零开始
                gdata.configSPS.zero_cal_thrust_running = True
            else:
                if gdata.configSPS2.zero_cal_thrust_running:
                    return
                # 标记调零开始
                gdata.configSPS2.zero_cal_thrust_running = True

            if self.fetch_button and self.fetch_button.page:
                self.fetch_button.visible = False
                self.fetch_button.update()

            if self.abort_button and self.abort_button.page:
                self.abort_button.visible = True
                self.abort_button.update()

            if self.seconds_tick and self.seconds_tick.page:
                for i in range(20, 0, -1):
                    is_running = gdata.configSPS.zero_cal_thrust_running if self.name == 'sps' else gdata.configSPS2.zero_cal_thrust_running
                    if is_running == False:
                        return

                    self.seconds_tick.value = f'{i}s'
                    self.seconds_tick.update()
                    await asyncio.sleep(1)

                # 时间到，调零结束
                if self.name == 'sps':
                    average_ad1 = JM3846ThrustUtil.get_avg(gdata.configSPS.zero_cal_ad1_for_thrust, self.name)
                    mv_per_v = JM3846Calculator.calculate_mv_per_v(average_ad1, gdata.configSPS.gain_1)
                    self.seconds_tick.value = round(mv_per_v, 4)
                elif self.name == 'sps2':
                    average_ad1 = JM3846ThrustUtil.get_avg(gdata.configSPS2.zero_cal_ad1_for_thrust, self.name)
                    mv_per_v = JM3846Calculator.calculate_mv_per_v(average_ad1, gdata.configSPS2.gain_1)
                    self.seconds_tick.value = round(mv_per_v, 4)
                self.seconds_tick.update()

                # 正常情况下执行到这里，需要回调on_finish方法
                if self.on_finish_callback:
                    self.on_finish_callback(round(mv_per_v, 4))

        except:
            logging.exception(
                "exception occured at ZeroCalExecutorThrust.on_tick")

        finally:
            if self.name == 'sps':
                gdata.configSPS.zero_cal_thrust_running = False
                gdata.configSPS.zero_cal_ad1_for_thrust.clear()
            else:
                gdata.configSPS2.zero_cal_thrust_running = False
                gdata.configSPS2.zero_cal_ad1_for_thrust.clear()

    def reset(self):
        self.on_abort()

    def will_unmount(self):
        if self.tick_task:
            self.tick_task.cancel()
