import logging
import flet as ft
import asyncio
from typing import Literal
from db.models.counter_log import CounterLog
from .display import CounterDisplay
from db.models.preference import Preference
from db.models.date_time_conf import DateTimeConf
from common.global_data import gdata


class ManuallyCounter(ft.Container):
    def __init__(self, name: Literal['sps1', 'sps2']):
        super().__init__()
        self.expand = True
        self.name = name

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

    def __on_start(self, e):
        counter_log = CounterLog.get_or_none(CounterLog.sps_name == self.name, CounterLog.counter_type == 1)
        # if count log exists, delete it
        if counter_log is not None:
            self.__delete_counter_log()

        # and then create new count log
        CounterLog.create(sps_name=self.name, counter_type=1, start_utc_date_time=gdata.utc_date_time, counter_status="running")
        self.__calculate()

    def __on_stop(self, e):
        CounterLog.update(counter_status="reset", stop_utc_date_time=gdata.utc_date_time).where(CounterLog.sps_name == self.name, CounterLog.counter_type == 1).execute()
        self.__calculate()

    def __on_resume(self, e):
        self.__delete_counter_log()
        e.page.close(self.dlg_modal)
        self.__calculate()

    def __delete_counter_log(self):
        CounterLog.delete().where(CounterLog.sps_name == self.name, CounterLog.counter_type == 1).execute()

    def __create_dlg_modal(self):
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text(self.page.session.get('lang.counter.please_confirm')),
            content=ft.Text(self.page.session.get('lang.counter.do_you_really_want_to_reset_counter')),
            actions=[
                ft.TextButton(self.page.session.get('lang.counter.yes'), on_click=lambda e: self.__on_resume(e)),
                ft.TextButton(
                    text=self.page.session.get('lang.counter.no'),
                    on_click=lambda e: e.page.close(self.dlg_modal)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

    def build(self):
        self.__create_dlg_modal()

        self.display = CounterDisplay()

        self.started_at = ft.Text("", visible=False)
        self.time_elapsed = ft.Text("", visible=False)
        self.stopped_at = ft.Text("", visible=False)

        self.status_text = ft.Text(value=self.page.session.get('lang.counter.stopped'), color=ft.Colors.WHITE, size=12)

        self.status_container = ft.Container(
            content=self.status_text,
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.RED_500,
            border_radius=ft.border_radius.all(40),
            padding=ft.padding.only(top=0, bottom=4, left=10, right=10)
        )

        self.start_button = ft.FilledButton(
            text=self.page.session.get('lang.counter.start'),
            icon=ft.icons.PLAY_CIRCLE_OUTLINED,
            bgcolor=ft.Colors.GREEN,
            width=220,
            visible=False,
            on_click=lambda e: self.__on_start(e)
        )

        self.stop_button = ft.FilledButton(
            text=self.page.session.get('lang.counter.stop'),
            icon=ft.icons.STOP_CIRCLE_OUTLINED,
            bgcolor=ft.Colors.RED,
            width=220,
            visible=False,
            on_click=lambda e: self.__on_stop(e)
        )

        self.resume_button = ft.FilledButton(
            text=self.page.session.get('lang.counter.resume'),
            bgcolor=ft.Colors.ORANGE,
            icon=ft.icons.RESTART_ALT_OUTLINED,
            width=220,
            visible=False,
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
                self.resume_button
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

    def did_mount(self):
        self._task = self.page.run_task(self.__running)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    async def __running(self):
        while True:
            try:
                self.__calculate()
            except Exception as e:
                logging.exception(e)
            await asyncio.sleep(self.interval)

    def __calculate(self):
        average_power = 0
        average_speed = 0

        counter_log: CounterLog = CounterLog.get_or_none(CounterLog.sps_name == self.name, CounterLog.counter_type == 1)
        if counter_log is None or counter_log.counter_status == "stopped":
            self.status_text.value = self.page.session.get('lang.counter.stopped')
            self.status_container.bgcolor = ft.Colors.RED_500
            self.status_container.update()

            self.started_at.visible = False
            self.time_elapsed.visible = False
            self.stopped_at.visible = False
            self.infos.update()

            self.start_button.visible = True
            self.stop_button.visible = False
            self.resume_button.visible = False
            self.buttons.update()

            self.display.set_average_power(0, self.system_unit)
            self.display.set_total_energy(0, self.system_unit)
            self.display.set_average_speed(0)
            return

        if counter_log.counter_status == "reset":
            self.status_text.value = self.page.session.get('lang.counter.reset')
            self.status_container.bgcolor = ft.Colors.ORANGE_500
            self.status_container.update()

            self.stopped_at.value = f'{self.page.session.get("lang.counter.stopped_at")} {counter_log.stop_utc_date_time.strftime(self.date_format)}'
            self.stopped_at.visible = True
            self.started_at.visible = False
            self.time_elapsed.visible = True
            self.infos.update()
            self.start_button.visible = False
            self.stop_button.visible = False
            self.resume_button.visible = True
            self.buttons.update()
            return

        # the rest of the code is for the running status
        self.status_text.value = self.page.session.get('lang.counter.running')
        self.status_container.bgcolor = ft.Colors.GREEN_500
        self.status_container.update()

        self.started_at.value = f'{self.page.session.get("lang.counter.started_at")} {counter_log.start_utc_date_time.strftime(self.date_format)}'
        self.started_at.visible = True
        self.time_elapsed.visible = True
        self.stopped_at.visible = False
        self.infos.update()

        self.start_button.visible = False
        self.stop_button.visible = True
        self.resume_button.visible = False
        self.buttons.update()

        start_time = counter_log.start_utc_date_time
        end_time = gdata.utc_date_time

        if counter_log.times != 0:
            average_power = counter_log.total_power / counter_log.times
            average_speed = counter_log.total_speed / counter_log.times

        hours = (end_time - start_time).total_seconds() / 3600

        total_energy = average_power * hours / 1000  # kWh

        time_elapsed = end_time - start_time
        days = time_elapsed.days
        hours = time_elapsed.seconds // 3600
        minutes = (time_elapsed.seconds % 3600) // 60
        seconds = time_elapsed.seconds % 60

        time_elapsed = f'{days:02d} d {hours:02d}:{minutes:02d}:{seconds:02d} h'
        self.time_elapsed.value = f'{time_elapsed} {self.page.session.get("lang.counter.measured")}'
        self.time_elapsed.update()

        self.display.set_average_power(average_power, self.system_unit)
        self.display.set_total_energy(total_energy, self.system_unit)
        self.display.set_average_speed(average_speed)
