import logging
import flet as ft
from ui.home.dashboard.meters.speed_meter import SpeedMeter
from ui.home.dashboard.meters.power_meter import PowerMeter
from ui.home.dashboard.meters.torque_meter import TorqueMeter
from ui.common.simple_card import SimpleCard


class SingleMeters(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True

    def get_radius(self, radio):
        try:
            if self.page is None:
                return 0

            return self.page.height * radio
        except:
            logging.exception('exception occured at SingleMeters.build')

        return 0

    def build(self):
        try:
            self.speed_meter = SpeedMeter("sps", self.get_radius(0.16))
            self.power_meter = PowerMeter("sps", self.get_radius(0.22))
            self.torque_meter = TorqueMeter("sps", self.get_radius(0.16))

            row = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                controls=[
                    SimpleCard(
                        body=self.speed_meter,
                        body_bottom_right=False,
                        expand=False
                    ),
                    SimpleCard(
                        body=self.power_meter,
                        body_bottom_right=False,
                        expand=False
                    ),
                    SimpleCard(
                        body=self.torque_meter,
                        body_bottom_right=False,
                        expand=False
                    )
                ]
            )

            self.content = ft.Column(
                expand=True,
                run_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[row]
            )
        except:
            logging.exception('exception occured at SingleMeters.build')

    def reload(self):
        try:
            if self.speed_meter:
                self.speed_meter.reload()

            if self.power_meter:    
                self.power_meter.reload()

            if self.torque_meter:    
                self.torque_meter.reload()
        except:
            logging.exception('exception occured at SingleMeters.reload')
