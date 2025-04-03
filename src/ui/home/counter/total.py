import asyncio
from typing import Literal
import flet as ft
from db.models.preference import Preference
from ui.common.simple_card import SimpleCard
from .display import CounterDisplay


class CounterTotal(ft.Container):
    def __init__(self, name: Literal['SPS1', 'SPS2']):
        super().__init__()
        self.expand = True
        self.name = name
        self.system_unit = Preference.get().system_unit

    def build(self):
        self.display = CounterDisplay()
        time_elapsed = ft.Text("00 d 23:10:01 h measured")
        started_at = ft.Text("started at 18/07/2014 06:56:19")

        self.content = SimpleCard(
            title="Total",
            expand=False,
            body=ft.Column(
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.display,
                    time_elapsed,
                    started_at
                ]))

    async def __refresh_data(self):
        while True:
            result = self.page.session.get(f'counter_total_{self.name}')
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

    def did_mount(self):
        self._task = self.page.run_task(self.__refresh_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()
