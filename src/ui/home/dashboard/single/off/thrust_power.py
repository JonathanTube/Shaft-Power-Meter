import flet as ft
import asyncio
from db.models.data_log import DataLog
from utils.unit_parser import UnitParser


class ThrustPower(ft.Container):
    def __init__(self):
        super().__init__()
        self.right = 10
        self.top = 10

    def did_mount(self):
        self._task = self.page.run_task(self.__load_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    async def __load_data(self):
        while True:
            data_log = DataLog.select(
                DataLog.thrust
            ).where(
                DataLog.name == "SPS1"
            ).order_by(DataLog.id.desc()).first()

            if data_log:
                thrust_and_unit = UnitParser.parse_power(data_log.thrust)
                thrust = thrust_and_unit[0]
                self.thrust_value.value = thrust
                self.thrust_value.update()
                unit = thrust_and_unit[1]
                self.thrust_unit.value = unit
                self.thrust_unit.update()
            await asyncio.sleep(1)

    def build(self):
        self.thrust_value = ft.Text("0")
        self.thrust_unit = ft.Text("W")
        self.content = ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Thrust Power", weight=ft.FontWeight.W_500),
                ft.Row(controls=[self.thrust_value, self.thrust_unit])
            ],
            expand=True
        )
