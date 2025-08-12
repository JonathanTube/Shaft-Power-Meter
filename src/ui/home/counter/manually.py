import logging
import flet as ft
import asyncio
from typing import Literal
from asyncio import to_thread
from db.models.counter_log import CounterLog
from .display import CounterDisplay
from db.models.preference import Preference
from db.models.date_time_conf import DateTimeConf
from common.global_data import gdata


class ManuallyCounter(ft.Container):
    def __init__(self, name: Literal['sps', 'sps2']):
        super().__init__()
        self.expand = True
        self.name = name
        self._task = None
        self.task_running = False

        self.height = 280
        self.border_radius = ft.border_radius.all(10)
        self.padding = 10
        self.border = ft.border.all(
            width=0.5,
            color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE)
        )

        preference: Preference = Preference.get()
        datetime_conf: DateTimeConf = DateTimeConf.get()
        self.system_unit = preference.system_unit
        self.interval = preference.data_refresh_interval
        self.date_format = f'{datetime_conf.date_format} %H:%M:%S'

    async def __on_start(self, e):
        try:
            await to_thread(CounterLog.delete().where(
                CounterLog.sps_name == self.name,
                CounterLog.counter_type == 1
            ).execute)

            await to_thread(CounterLog.create,
                sps_name=self.name,
                counter_type=1,
                start_utc_date_time=gdata.configDateTime.utc,
                counter_status="running"
            )
            await self.__calculate_async()
        except Exception:
            logging.exception('exception occured at ManuallyCounter.__on_start')

    async def __on_stop(self, e):
        try:
            await to_thread(CounterLog.update(
                counter_status="reset",
                stop_utc_date_time=gdata.configDateTime.utc
            ).where(
                CounterLog.sps_name == self.name,
                CounterLog.counter_type == 1
            ).execute)
            await self.__calculate_async()
        except Exception:
            logging.exception('exception occured at ManuallyCounter.__on_stop')

    async def __on_resume(self, e):
        try:
            if e.page is not None:
                await to_thread(CounterLog.delete().where(
                    CounterLog.sps_name == self.name,
                    CounterLog.counter_type == 1
                ).execute)
                e.page.close(self.dlg_modal)
                await self.__calculate_async()
        except Exception:
            logging.exception('exception occured at ManuallyCounter.__on_resume')

    def __create_dlg_modal(self):
        if self.page and self.page.session:
            self.dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text(self.page.session.get('lang.counter.please_confirm')),
                content=ft.Text(self.page.session.get('lang.counter.do_you_really_want_to_reset_counter')),
                actions=[
                    ft.TextButton(
                        self.page.session.get('lang.counter.yes'),
                        on_click=lambda e: asyncio.create_task(self.__on_resume(e))
                    ),
                    ft.TextButton(
                        text=self.page.session.get('lang.counter.no'),
                        on_click=lambda e: e.page.close(self.dlg_modal)
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )

    def build(self):
        try:
            self.__create_dlg_modal()

            self.display = CounterDisplay()
            self.started_at = ft.Text("", visible=False)
            self.time_elapsed = ft.Text("", visible=False)
            self.stopped_at = ft.Text("", visible=False)

            self.status_text = ft.Text(value=self.page.session.get('lang.counter.stopped'),
                                       color=ft.Colors.WHITE, size=12)
            self.status_container = ft.Container(
                content=self.status_text,
                alignment=ft.alignment.center,
                bgcolor=ft.Colors.RED_500,
                border_radius=ft.border_radius.all(40),
                padding=ft.padding.only(top=0, bottom=4, left=10, right=10)
            )

            self.start_button = ft.FilledButton(
                text=self.page.session.get('lang.counter.start'),
                icon=ft.Icons.PLAY_CIRCLE_OUTLINED,
                icon_color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN,
                color=ft.Colors.WHITE,
                width=220,
                visible=False,
                on_click=lambda e: asyncio.create_task(self.__on_start(e))
            )
            self.stop_button = ft.FilledButton(
                text=self.page.session.get('lang.counter.stop'),
                icon=ft.Icons.STOP_CIRCLE_OUTLINED,
                icon_color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED,
                color=ft.Colors.WHITE,
                width=220,
                visible=False,
                on_click=lambda e: asyncio.create_task(self.__on_stop(e))
            )
            self.reset_button = ft.FilledButton(
                text=self.page.session.get('lang.counter.reset'),
                bgcolor=ft.Colors.ORANGE,
                icon_color=ft.Colors.WHITE,
                color=ft.Colors.WHITE,
                icon=ft.Icons.RESTART_ALT_OUTLINED,
                width=220,
                visible=False,
                on_click=lambda e: e.page.open(self.dlg_modal)
            )

            self.title = ft.Text(self.page.session.get('lang.counter.manually'),
                                 weight=ft.FontWeight.BOLD, size=16)

            self.infos = ft.Column(expand=True, spacing=0,
                                   horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                   alignment=ft.MainAxisAlignment.CENTER,
                                   controls=[self.time_elapsed, self.started_at, self.stopped_at])
            self.buttons = ft.Column(expand=True,
                                     horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                     alignment=ft.MainAxisAlignment.CENTER,
                                     controls=[self.start_button, self.stop_button, self.reset_button])
            self.content = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                     alignment=ft.MainAxisAlignment.CENTER,
                                     spacing=5 if self.page.window.height <= 600 else 20,
                                     controls=[
                                         ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                controls=[self.title, self.status_container]),
                                         self.display,
                                         self.infos,
                                         self.buttons
                                     ])
        except Exception:
            logging.exception('exception occured at ManuallyCounter.build')

    def did_mount(self):
        self.task_running = True
        if self.page:
            self._task = self.page.run_task(self.__running)

    def will_unmount(self):
        self.task_running = False
        if self._task:
            self._task.cancel()

    async def __running(self):
        while self.task_running:
            try:
                await self.__calculate_async()
            except Exception:
                logging.exception("exception occured at ManuallyCounter.__running")
            await asyncio.sleep(self.interval)

    async def __calculate_async(self):
        try:
            counter_log = await to_thread(
                CounterLog.get_or_none,
                (CounterLog.sps_name == self.name) & (CounterLog.counter_type == 1)
            )

            # ... 原有 UI 更新逻辑（去掉中途的多次 update，改为最后 self.update() 一次）
            # 示例：
            if counter_log is None or counter_log.counter_status == "stopped":
                self.status_text.value = self.page.session.get('lang.counter.stopped')
                self.status_container.bgcolor = ft.Colors.RED_500
                self.started_at.visible = False
                self.time_elapsed.visible = False
                self.stopped_at.visible = False
                self.start_button.visible = True
                self.stop_button.visible = False
                self.reset_button.visible = False
                self.display.set_average_power(0, self.system_unit)
                self.display.set_total_energy(0, self.system_unit)
                self.display.set_average_speed(0)
                self.update()
                return

            # 其余状态逻辑同理...
            self.update()

        except Exception:
            logging.exception("exception occured at ManuallyCounter.__calculate_async")
