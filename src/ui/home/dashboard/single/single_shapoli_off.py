import flet as ft

from ui.common.meter_round import MeterRound


class SingleShaPoLiOff(ft.Container):
    def __init__(self):
        super().__init__()
        self.content = self.__create()
        self.padding = ft.padding.only(left=40)

    def __create(self):
        self.speed_meter = MeterRound(
            heading="Speed", radius=100, value=80, max_value=100, limit_value=90, unit="rpm"
        )
        self.power_meter = MeterRound(
            heading="Power", radius=120, value=80, max_value=100, limit_value=90, unit="kW"
        )
        self.torque_meter = MeterRound(
            heading="Torque", radius=100, value=80, max_value=100, limit_value=90, unit="kNm"
        )
        return ft.Row(
            # expand=True,
            # alignment=ft.MainAxisAlignment.CENTER,
            # vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                self.speed_meter,
                self.power_meter,
                self.torque_meter
            ])
