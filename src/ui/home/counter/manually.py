import flet as ft
import logging
import asyncio
from typing import Literal
from .display import CounterDisplay
from common.global_data import gdata


class ManuallyCounter(ft.Container):
    def __init__(self, name: Literal['sps', 'sps2']):
        super().__init__()
        self.name = name

        self.height = 280
        self.expand = True
        self.border_radius = ft.border_radius.all(10)
        self.padding = 10
        self.border = ft.border.all(width=0.5, color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE))

        self.task = None
        self.task_running = False

        self.system_unit = gdata.configPreference.system_unit
        self.interval = gdata.configPreference.data_refresh_interval
        self.date_format = f'{gdata.configDateTime.date_format} %H:%M:%S'

        self.start_time = gdata.configCounterSPS.Manually.start_at if self.name == 'sps' else gdata.configCounterSPS.Manually.start_at

    def build(self):
        try:
            self.dlg_modal = ft.AlertDialog(
                modal=True,
                title=ft.Text(self.page.session.get('lang.counter.please_confirm')),
                content=ft.Text(self.page.session.get('lang.counter.do_you_really_want_to_reset_counter')),
                actions=[
                    ft.TextButton(self.page.session.get('lang.counter.yes'), on_click=lambda _: self.on_resume()),
                    ft.TextButton(text=self.page.session.get('lang.counter.no'), on_click=lambda e: e.page.close(self.dlg_modal))
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )

            self.display = CounterDisplay()

            self.started_at = ft.Text("",)
            self.time_elapsed = ft.Text("")
            self.stopped_at = ft.Text("")

            self.status_text = ft.Text(value="", color=ft.Colors.WHITE, size=12)

            self.status_container = ft.Container(
                content=self.status_text,
                alignment=ft.alignment.center,
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
                on_click=lambda _: self.on_start()
            )

            self.stop_button = ft.FilledButton(
                text=self.page.session.get('lang.counter.stop'),
                icon=ft.Icons.STOP_CIRCLE_OUTLINED,
                icon_color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED,
                color=ft.Colors.WHITE,
                width=220,
                on_click=lambda _: self.on_stop()
            )

            self.reset_button = ft.FilledButton(
                text=self.page.session.get('lang.counter.reset'),
                bgcolor=ft.Colors.ORANGE,
                icon_color=ft.Colors.WHITE,
                color=ft.Colors.WHITE,
                icon=ft.Icons.RESTART_ALT_OUTLINED,
                width=220,
                on_click=lambda e: e.page.open(self.dlg_modal)
            )

            self.title = ft.Text(self.page.session.get('lang.counter.manually'), weight=ft.FontWeight.BOLD, size=16)

            self.infos = ft.Column(
                expand=True,
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.time_elapsed,
                    self.started_at,
                    self.stopped_at
                ]
            )

            self.buttons = ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.start_button,
                    self.stop_button,
                    self.reset_button
                ]
            )

            self.content = ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=5 if self.page.window.height <= 600 else 20,
                controls=[
                    ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[self.title, self.status_container]),
                    self.display,
                    self.infos,
                    self.buttons
                ]
            )

            self.set_style()
        except:
            logging.exception('ManuallyCounter.build')

    def on_start(self):
        if self.name == 'sps':
            gdata.configCounterSPS.Manually.status = 'running'
        else:
            gdata.configCounterSPS2.Manually.status = 'running'
        self.set_style()
        self.update()

    def on_stop(self):
        if self.name == 'sps':
            gdata.configCounterSPS.Manually.status = 'reset'
        else:
            gdata.configCounterSPS2.Manually.status = 'reset'
        self.set_style()
        self.update()

    def on_resume(self):
        if not self.page:
            return
        self.page.close(self.dlg_modal)

        if self.name == 'sps':
            gdata.configCounterSPS.Manually.status = 'stopped'
        else:
            gdata.configCounterSPS2.Manually.status = 'stopped'

        self.set_data(0, 0, 0.0)
        self.set_style()
        self.update()

    def did_mount(self):
        self.task_running = True
        if self.page:
            self._task = self.page.run_task(self.loop)

    def will_unmount(self):
        self.task_running = False
        if self._task:
            self._task.cancel()

    async def loop(self):
        while self.task_running:
            try:
                times = gdata.configCounterSPS.Manually.times if self.name == 'sps' else gdata.configCounterSPS2.Manually.times
                if times != 0:
                    return

                end_time = gdata.configDateTime.utc
                if not self.start_time:
                    return

                time_elapsed = end_time - self.start_time
                hours = time_elapsed.total_seconds() / 3600
                days = time_elapsed.days
                hours = time_elapsed.seconds // 3600
                minutes = (time_elapsed.seconds % 3600) // 60
                seconds = time_elapsed.seconds % 60
                time_elapsed = f'{days:02d} d {hours:02d}:{minutes:02d}:{seconds:02d} h'

                if self.time_elapsed and self.time_elapsed.page:
                    self.time_elapsed.value = f'{time_elapsed} {self.page.session.get("lang.counter.measured")}'
                    self.time_elapsed.update()

                # TODO:???
                total_power = gdata.configCounterSPS.Manually.total_power if self.name == 'sps' else gdata.configCounterSPS2.Manually.total_power
                total_energy = gdata.configCounterSPS.Manually.total_energy if self.name == 'sps' else gdata.configCounterSPS2.Manually.total_energy
                total_speed = gdata.configCounterSPS.Manually.total_speed if self.name == 'sps' else gdata.configCounterSPS2.Manually.total_speed

                self.set_data(total_power, total_energy, total_speed)
            except:
                logging.exception("ManuallyCounter.loop exception")
            finally:
                await asyncio.sleep(self.interval)

    def set_data(self, avg_power, total_energy, avg_speed):
        if self.display and self.display.page:
            self.display.set_average_power(avg_power, self.system_unit)
            self.display.set_total_energy(total_energy, self.system_unit)
            self.display.set_average_speed(avg_speed)
            self.display.update()

    def set_style(self):
        status = gdata.configCounterSPS.Manually.status if self.name == 'sps' else gdata.configCounterSPS2.Manually.status
        self.started_at.visible = status == 'running'
        self.time_elapsed.visible = status == 'reset'
        self.stopped_at.visible = status == 'reset'
        self.start_button.visible = status == 'stopped'
        self.stop_button.visible = status == 'running'
        self.reset_button.visible = status == 'reset'
        if status == 'stopped':
            self.status_text.value = self.page.session.get('lang.counter.stopped')
            self.status_container.bgcolor = ft.Colors.RED_500
        elif status == 'reset':
            self.status_text.value = self.page.session.get('lang.counter.reset')
            self.status_container.bgcolor = ft.Colors.ORANGE_500
            stopped_at = gdata.configCounterSPS.Manually.stop_at if self.name == 'sps' else gdata.configCounterSPS2.Manually.stop_at
            self.stopped_at.value = f'{self.page.session.get("lang.counter.stopped_at")} {stopped_at.strftime(self.date_format) if stopped_at else None}'
        elif status == 'running':
            self.status_text.value = self.page.session.get('lang.counter.running')
            self.status_container.bgcolor = ft.Colors.GREEN_500
            self.started_at.value = f'{self.page.session.get("lang.counter.started_at")} {self.start_time.strftime(self.date_format) if self.start_time else None}'
