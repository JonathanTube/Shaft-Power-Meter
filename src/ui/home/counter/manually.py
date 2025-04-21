import flet as ft
import asyncio
from typing import Literal
from datetime import datetime

from .display import CounterDisplay
from db.models.preference import Preference


class CounterManually(ft.Container):
    def __init__(self, name: Literal['sps1', 'sps2']):
        super().__init__()
        self.expand = True
        self.border_radius = ft.border_radius.all(10)
        self.padding = 10
        self.border = ft.border.all(
            width=0.5,
            color=ft.Colors.with_opacity(0.15, ft.Colors.INVERSE_SURFACE)   
        )

        self.name = name
        self._ui_refresh_task = None
        self._data_create_task = None
        self._task = None

        self.__load_config()

    def __load_config(self):
        self.system_unit = Preference.get().system_unit

    def __on_start(self, e):
        self.page.session.set(
            f'counter_manually_start_time_{self.name}', datetime.now())

        self.start_button.visible = False
        self.stop_button.visible = True
        self.resume_button.visible = False
        self.status_text.value = self.page.session.get('lang.counter.running')
        self.status_container.bgcolor = ft.Colors.GREEN_500 
        self.__start_task()
        self.content.update()

    def __on_stop(self, e):
        self.start_button.visible = False
        self.stop_button.visible = False
        self.resume_button.visible = True
        self.status_text.value = self.page.session.get('lang.counter.reset')
        self.status_container.bgcolor = ft.Colors.ORANGE_500

        self.stopped_at.value = f'{self.page.session.get("lang.counter.stopped_at")} {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        self.stopped_at.visible = True
        self.stopped_at.update()

        self.__stop_task()
        self.content.update()

    def __on_resume(self, e):
        self.start_button.visible = True
        self.stop_button.visible = False
        self.resume_button.visible = False
        self.status_text.value = self.page.session.get('lang.counter.stopped')
        self.status_container.bgcolor = ft.Colors.RED_500   
        self.time_elapsed.visible = False
        self.stopped_at.visible = False
        status_name = f'counter_manually_status_{self.name}'
        self.page.session.set(
            status_name, self.page.session.get('lang.counter.stopped'))
        self.display.set_average_power(0, self.system_unit)
        self.display.set_total_energy(0, self.system_unit)
        self.display.set_total_rounds(0)
        self.display.set_average_speed(0)
        e.page.close(self.dlg_modal)
        self.content.update()

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

        self.time_elapsed = ft.Text("", visible=False)
        self.stopped_at = ft.Text("", visible=False)

        status_name = f'counter_manually_status_{self.name}'
        status_value = self.page.session.get(status_name)

        if status_value is None:
            status_value = 'stopped'
            self.page.session.set(status_name, 'stopped')

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
            visible=status_value == 'stopped',
            on_click=lambda e: self.__on_start(e)
        )

        self.stop_button = ft.FilledButton(
            text=self.page.session.get('lang.counter.stop'),
            icon=ft.icons.STOP_CIRCLE_OUTLINED,
            bgcolor=ft.Colors.RED,
            width=220,
            visible=status_value == 'running',
            on_click=lambda e: self.__on_stop(e)
        )

        self.resume_button = ft.FilledButton(
            text=self.page.session.get('lang.counter.resume'),
            bgcolor=ft.Colors.ORANGE,
            icon=ft.icons.RESTART_ALT_OUTLINED,
            width=220,
            visible=status_value == 'Reset',
            on_click=lambda e: e.page.open(self.dlg_modal)
        )

        self.title = ft.Text(
            self.page.session.get('lang.counter.manually'),
            weight=ft.FontWeight.BOLD,
            size=16
        )

        self.content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        self.title,
                        self.status_container
                    ]),
                self.display,
                self.stopped_at,
                self.time_elapsed,
                self.start_button,
                self.stop_button,
                self.resume_button
            ]
        )

    def __start_task(self):
        status_name = f'counter_manually_status_{self.name}'
        start_time_name = f'counter_manually_start_time_{self.name}'
        status_value = self.page.session.get(status_name)
        if status_value == 'stopped':
            self._task = self.page.run_task(self.__refresh_data)
            self.page.session.set(status_name, 'running')
            self.page.session.set(start_time_name, datetime.now())

    def __stop_task(self):
        status_name = f'counter_manually_status_{self.name}'
        status_value = self.page.session.get(status_name)
        if status_value == 'running':
            self._task.cancel()
            self.page.session.set(status_name, 'reset')

    def did_mount(self):
        self.display.set_average_power(0, self.system_unit)
        self.display.set_total_energy(0, self.system_unit)
        self.display.set_total_rounds(0)
        self.display.set_average_speed(0)

        status_name = f'counter_manually_status_{self.name}'
        status_value = self.page.session.get(status_name)
        if status_value == 'running':
            self._task = self.page.run_task(self.__refresh_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    async def __refresh_data(self):
        while True:
            result = self.page.session.get(f'counter_manually_{self.name}')
            if result is not None:
                average_power = result['average_power']
                total_energy = result['total_energy']
                total_rounds = result['total_rounds']
                average_speed = result['average_speed']
                # print(average_power, total_energy, total_rounds, average_speed)

                self.time_elapsed.value = f'{result["time_elapsed"]} {self.page.session.get("lang.counter.measured")}'
                self.time_elapsed.visible = True
                self.time_elapsed.update()

                self.display.set_average_power(average_power, self.system_unit)
                self.display.set_total_energy(total_energy, self.system_unit)
                self.display.set_total_rounds(total_rounds)
                self.display.set_average_speed(average_speed)

            await asyncio.sleep(1)
