import flet as ft
import asyncio
from typing import Literal
from db.models.data_log import DataLog
from .display import CounterDisplay
from db.models.preference import Preference
from db.models.date_time_conf import DateTimeConf
from common.global_data import gdata
from peewee import fn


class ManuallyCounter(ft.Container):
    def __init__(self, name: Literal['sps1', 'sps2']):
        super().__init__()
        self.expand = True
        self.name = name

        self.border_radius = ft.border_radius.all(10)
        self.padding = 10
        self.border = ft.border.all(
            width=0.5,
            color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE)
        )

        self._task = None

        preference: Preference = Preference.get()
        datetime_conf: DateTimeConf = DateTimeConf.get()
        self.system_unit = preference.system_unit
        self.interval = preference.data_refresh_interval
        self.date_format = datetime_conf.date_format

    def __on_start(self, e):
        current_status = gdata.sps1_manually_status if self.name == 'sps1' else gdata.sps2_manually_status
        if current_status != 'stopped':
            return
        self._task = self.page.run_task(self.__running)

        if self.name == 'sps1':
            gdata.sps1_manually_start_time = gdata.utc_date_time
            gdata.sps1_manually_status = 'running'
        else:
            gdata.sps2_manually_start_time = gdata.utc_date_time
            gdata.sps2_manually_status = 'running'

        self.start_button.visible = False
        self.stop_button.visible = True
        self.resume_button.visible = False
        self.status_text.value = self.page.session.get('lang.counter.running')
        self.status_container.bgcolor = ft.Colors.GREEN_500
        self.started_at.value = f'{self.page.session.get("lang.counter.started_at")} {gdata.utc_date_time.strftime(self.date_format)}'
        self.started_at.visible = True
        self.content.update()

    def __on_stop(self, e):
        current_status = gdata.sps1_manually_status if self.name == 'sps1' else gdata.sps2_manually_status
        if current_status != 'running':
            return

        self._task.cancel()
        if self.name == 'sps1':
            gdata.sps1_manually_status = 'reset'
        else:
            gdata.sps2_manually_status = 'reset'

        self.start_button.visible = False
        self.stop_button.visible = False
        self.resume_button.visible = True
        self.status_text.value = self.page.session.get('lang.counter.reset')
        self.status_container.bgcolor = ft.Colors.ORANGE_500

        self.stopped_at.value = f'{self.page.session.get("lang.counter.stopped_at")} {gdata.utc_date_time.strftime(self.date_format)}'
        self.stopped_at.visible = True
        self.stopped_at.update()
        self.content.update()

    def __on_resume(self, e):
        current_status = gdata.sps1_manually_status if self.name == 'sps1' else gdata.sps2_manually_status
        if current_status != 'reset':
            return

        if self.name == 'sps1':
            gdata.sps1_manually_status = 'stopped'
        else:
            gdata.sps2_manually_status = 'stopped'

        self.start_button.visible = True
        self.stop_button.visible = False
        self.resume_button.visible = False
        self.status_text.value = self.page.session.get('lang.counter.stopped')
        self.status_container.bgcolor = ft.Colors.RED_500
        self.time_elapsed.visible = False
        self.stopped_at.visible = False

        self.display.set_average_power(0, self.system_unit)
        self.display.set_total_energy(0, self.system_unit)
        self.display.set_total_rounds(0)
        self.display.set_average_speed(0)
        self.content.update()
        e.page.close(self.dlg_modal)

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
        current_status = gdata.sps1_manually_status if self.name == 'sps1' else gdata.sps2_manually_status
        self.__create_dlg_modal()

        self.display = CounterDisplay()

        self.started_at = ft.Text("", visible=False)
        self.time_elapsed = ft.Text("", visible=False)
        self.stopped_at = ft.Text("", visible=False)

        self.status_text = ft.Text(
            value=self.page.session.get('lang.counter.stopped'),
            size=12
        )
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
            visible=current_status == 'stopped',
            on_click=lambda e: self.__on_start(e)
        )

        self.stop_button = ft.FilledButton(
            text=self.page.session.get('lang.counter.stop'),
            icon=ft.icons.STOP_CIRCLE_OUTLINED,
            bgcolor=ft.Colors.RED,
            width=220,
            visible=current_status == 'running',
            on_click=lambda e: self.__on_stop(e)
        )

        self.resume_button = ft.FilledButton(
            text=self.page.session.get('lang.counter.resume'),
            bgcolor=ft.Colors.ORANGE,
            icon=ft.icons.RESTART_ALT_OUTLINED,
            width=220,
            visible=current_status == 'reset',
            on_click=lambda e: e.page.open(self.dlg_modal)
        )

        self.title = ft.Text(self.page.session.get('lang.counter.manually'), weight=ft.FontWeight.BOLD, size=16)

        self.content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[self.title, self.status_container]),
                self.display,
                self.started_at,
                self.stopped_at,
                self.time_elapsed,
                self.start_button,
                self.stop_button,
                self.resume_button
            ]
        )

    def did_mount(self):
        self.display.set_average_power(0, self.system_unit)
        self.display.set_total_energy(0, self.system_unit)
        self.display.set_total_rounds(0)
        self.display.set_average_speed(0)

        current_status = gdata.sps1_manually_status if self.name == 'sps1' else gdata.sps2_manually_status
        if current_status == 'running':
            self._task = self.page.run_task(self.__running)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    async def __running(self):
        while True:
            end_time = gdata.utc_date_time
            start_time = gdata.sps1_manually_start_time if self.name == 'sps1' else gdata.sps2_manually_start_time
            data_log = DataLog.select(
                fn.COALESCE(fn.AVG(DataLog.power), 0).alias('average_power'),
                fn.COALESCE(fn.MIN(DataLog.rounds), 0).alias('min_rounds'),
                fn.COALESCE(fn.MAX(DataLog.rounds), 0).alias('max_rounds'),
            ).where(
                DataLog.name == self.name,
                DataLog.utc_date_time >= start_time,
                DataLog.utc_date_time <= end_time
            ).dicts().get()

            average_power = data_log['average_power']
            max_rounds = data_log['max_rounds']
            min_rounds = data_log['min_rounds']

            hours = (end_time - start_time).total_seconds() / 3600

            total_energy = average_power * hours / 1000  # kWh

            total_rounds = max_rounds - min_rounds

            average_speed = 0
            if hours > 0:
                average_speed = round(total_rounds / (hours * 60), 1)

            time_elapsed = end_time - start_time
            days = time_elapsed.days
            hours = time_elapsed.seconds // 3600
            minutes = (time_elapsed.seconds % 3600) // 60
            seconds = time_elapsed.seconds % 60

            time_elapsed = f'{days:02d} d {hours:02d}:{minutes:02d}:{seconds:02d} h'

            self.time_elapsed.value = f'{time_elapsed} {self.page.session.get("lang.counter.measured")}'
            self.time_elapsed.visible = True
            self.time_elapsed.update()

            self.display.set_average_power(average_power, self.system_unit)
            self.display.set_total_energy(total_energy, self.system_unit)
            self.display.set_total_rounds(total_rounds)
            self.display.set_average_speed(average_speed)

            await asyncio.sleep(self.interval)
