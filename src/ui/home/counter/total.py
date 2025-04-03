import asyncio
from typing import Literal
import flet as ft
from db.models.preference import Preference
from .display import CounterDisplay


class CounterTotal(ft.Container):
    def __init__(self, name: Literal['SPS1', 'SPS2']):
        super().__init__()
        self.expand = True
        self.border_radius = ft.border_radius.all(10)
        self.padding = 10
        self.border = ft.border.all(
            width=0.5,
            color=ft.colors.with_opacity(0.15, ft.colors.INVERSE_SURFACE)
        )

        self.name = name

        self._task = None

        self.system_unit = Preference.get().system_unit

    def build(self):
        self.display = CounterDisplay()
        self.time_elapsed = ft.Text("")
        self.started_at = ft.Text("")

        self.title = ft.Text('Total', weight=ft.FontWeight.BOLD, size=16)

        self.status_container = ft.Container(
            content=ft.Text(value='Running', size=14),
            alignment=ft.alignment.center,
            bgcolor=ft.colors.GREEN_500,
            border_radius=ft.border_radius.all(40),
            padding=ft.padding.only(top=0, bottom=4, left=10, right=10)
        )

        self.content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                       controls=[
                           self.title,
                           self.status_container
                       ]),
                self.display,
                self.time_elapsed,
                self.started_at
            ])

    async def __refresh_data(self):
        while True:
            result = self.page.session.get(f'counter_total_{self.name}')
            if result is not None:
                average_power = result['average_power']
                total_energy = result['total_energy']
                total_rounds = result['total_rounds']
                average_speed = result['average_speed']

                self.time_elapsed.value = result['time_elapsed']
                self.time_elapsed.visible = True
                self.time_elapsed.update()

                self.started_at.value = result['started_at']
                self.started_at.visible = True
                self.started_at.update()

                self.display.set_average_power(average_power, self.system_unit)
                self.display.set_total_energy(total_energy, self.system_unit)
                self.display.set_total_rounds(total_rounds)
                self.display.set_average_speed(average_speed)

            await asyncio.sleep(Preference.get().data_refresh_interval)

    def did_mount(self):
        self._task = self.page.run_task(self.__refresh_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()
