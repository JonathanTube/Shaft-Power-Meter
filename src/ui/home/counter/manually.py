import flet as ft
import asyncio
from typing import Literal
from datetime import datetime

from ui.common.simple_card import SimpleCard
from .display import CounterDisplay
from db.models.preference import Preference


class CounterManually(ft.Container):
    def __init__(self, name: Literal['SPS1', 'SPS2']):
        super().__init__()
        self.expand = True
        self.name = name
        self._ui_refresh_task = None
        self._data_create_task = None

        self.__load_config()

    def __load_config(self):
        self.system_unit = Preference.get().system_unit

    def __on_start(self, e):
        self.page.session.set(
            f'counter_manually_start_time_{self.name}', datetime.now())

        self.start_button.visible = False
        self.stop_button.visible = True
        self.resume_button.visible = False
        self.status_text.value = 'Running'
        self.status_text.color = ft.Colors.GREEN
        self.__start_task()
        self.content.update()

    def __on_stop(self, e):
        self.start_button.visible = False
        self.stop_button.visible = False
        self.resume_button.visible = True
        self.status_text.value = 'Reset'
        self.status_text.color = ft.Colors.ORANGE
        self.__stop_task()
        self.content.update()

    def __on_resume(self, e):
        self.start_button.visible = True
        self.stop_button.visible = False
        self.resume_button.visible = False
        self.status_text.value = 'Stopped'
        self.status_text.color = ft.Colors.RED
        status_name = f'counter_manually_status_{self.name}'
        self.page.session.set(status_name, 'stopped')
        self.display.set_average_power(0, self.system_unit)
        self.display.set_total_energy(0, self.system_unit)
        self.display.set_total_rounds(0)
        self.display.set_average_speed(0)
        e.page.close(self.dlg_modal)
        self.content.update()

    def __create_dlg_modal(self):
        self.dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text("Do you really want to reset the counter?"),
            actions=[
                ft.TextButton("Yes", on_click=lambda e: self.__on_resume(e)),
                ft.TextButton(
                    text="No",
                    on_click=lambda e: e.page.close(self.dlg_modal)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

    def build(self):
        self.__create_dlg_modal()

        self.display = CounterDisplay()

        stopped_at = ft.Text("Stopped", weight=ft.FontWeight.BOLD,
                             color=ft.Colors.RED)
        time_elapsed = ft.Text("00 d 23:10:01 h measured")
        stopped_at = ft.Text("stopped at 18/07/2014 06:56:19")

        status_name = f'counter_manually_status_{self.name}'
        status_value = self.page.session.get(status_name)

        if status_value is None:
            status_value = 'stopped'
            self.page.session.set(status_name, status_value)

        self.status_text = ft.Text(
            value=status_value,
            size=14,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.RED
        )

        self.start_button = ft.FilledButton(
            text="Start",
            bgcolor=ft.Colors.GREEN,
            width=220,
            visible=status_value == 'stopped',
            on_click=lambda e: self.__on_start(e)
        )

        self.stop_button = ft.FilledButton(
            text="Stop",
            bgcolor=ft.Colors.RED,
            width=220,
            visible=status_value == 'running',
            on_click=lambda e: self.__on_stop(e)
        )

        self.resume_button = ft.FilledButton(
            text="Resume",
            bgcolor=ft.Colors.ORANGE,
            width=220,
            visible=status_value == 'reset',
            on_click=lambda e: e.page.open(self.dlg_modal)
        )

        self.content = SimpleCard(
            title="Manually",
            expand=False,
            body=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.display,
                    self.status_text,
                    # stopped_at,
                    # time_elapsed,
                    self.start_button,
                    self.stop_button,
                    self.resume_button
                ]
            )
        )

    def __start_task(self):
        status_name = f'counter_manually_status_{self.name}'
        start_time_name = f'counter_manually_start_time_{self.name}'
        print(f'status_name: {status_name}')
        status_value = self.page.session.get(status_name)
        print(f'status_value: {status_value}')
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
            print(f'result: {result}')
            if result is not None:
                average_power = result['average_power']
                total_energy = result['total_energy']
                total_rounds = result['total_rounds']
                average_speed = result['average_speed']

                self.display.set_average_power(average_power, self.system_unit)
                self.display.set_total_energy(total_energy, self.system_unit)
                self.display.set_total_rounds(total_rounds)
                self.display.set_average_speed(average_speed)

            await asyncio.sleep(Preference.get().data_refresh_interval)
