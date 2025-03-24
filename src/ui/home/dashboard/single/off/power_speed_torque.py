import flet as ft

from db.models.data_log import DataLog
from ui.common.meter_round import MeterRound
import asyncio
from utils.unit_parser import UnitParser
from db.models.limitations import Limitations


class PowerSpeedTorque(ft.Container):
    def __init__(self):
        super().__init__()
        self.__load_settings()

    def did_mount(self):
        self._task = self.page.run_task(self.__load_data)

    def will_unmount(self):
        if self._task:
            self._task.cancel()

    def __load_settings(self):
        limitations = Limitations.get_or_none()
        print(f'limitations: {limitations}')
        if limitations:
            self.speed_max = limitations.speed_max
            self.speed_warning = limitations.speed_warning

            self.power_max = limitations.power_max
            self.power_warning = limitations.power_warning

            self.torque_max = limitations.torque_max
            self.torque_warning = limitations.torque_warning

    async def __load_data(self):
        while True:
            data_log = DataLog.select().order_by(DataLog.id.desc()).first()
            if data_log:
                speed_and_unit = UnitParser.parse_speed(data_log.revolution)
                speed_value = speed_and_unit[0]
                speed_unit = speed_and_unit[1]
                self.speed_meter.set_data(
                    speed_value, speed_unit,
                    self.speed_max, self.speed_warning
                )

                power_and_unit = UnitParser.parse_power(data_log.power)
                power_value = power_and_unit[0]
                power_unit = power_and_unit[1]
                self.power_meter.set_data(
                    power_value, power_unit,
                    self.power_max, self.power_warning
                )

                torque_and_unit = UnitParser.parse_torque(data_log.torque)
                torque_value = torque_and_unit[0]
                torque_unit = torque_and_unit[1]
                self.torque_meter.set_data(
                    torque_value, torque_unit,
                    self.torque_max, self.torque_warning
                )

            await asyncio.sleep(1)

    def build(self):
        self.speed_meter = MeterRound(heading="Speed", radius=100, unit="rpm")
        self.power_meter = MeterRound(heading="Power", radius=120, unit="W")
        self.torque_meter = MeterRound(heading="Torque", radius=100, unit="Nm")
        self.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            controls=[
                self.speed_meter,
                self.power_meter,
                self.torque_meter
            ])
