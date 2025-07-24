import logging
import flet as ft

from ui.home.dashboard.meters.speed_meter import SpeedMeter
from ui.home.dashboard.meters.power_meter import PowerMeter
from ui.home.dashboard.meters.torque_meter import TorqueMeter
from ui.home.dashboard.thrust.index import ThrustBlock
from ui.common.simple_card import SimpleCard
from typing import Literal


class DualMeters(ft.Container):
    def __init__(self, name: Literal["sps", "sps2"]):
        super().__init__()
        self.expand = True
        self.name = name

    def get_radius(self, radio):
        try:
            if self.page is None or self.page.window is None:
                return 0

            radius = self.page.window.height * radio
            return radius * 0.62
        except:
            logging.exception('exception occured at DualMeters.get_radius')

        return 0

    def build(self):
        try:
            if self.page is None or self.page.session is None:
                return

            self.speed_meter = SpeedMeter(self.name, self.get_radius(0.22))
            self.power_meter = PowerMeter(self.name, self.get_radius(0.32))
            self.torque_meter = TorqueMeter(self.name, self.get_radius(0.22))
            self.thrust_meter = ThrustBlock(self.name)

            title = self.page.session.get("lang.common.sps")
            if self.name == "sps2":
                title = self.page.session.get("lang.common.sps2")

            self.content = ft.Stack(
                controls=[
                    ft.Text(value=title, size=18, weight=ft.FontWeight.BOLD, left=10, top=10),
                    self.thrust_meter,
                    SimpleCard(
                        body_bottom_right=False,
                        body=ft.Stack(
                            expand=True,
                            alignment=ft.alignment.center,
                            controls=[
                                ft.Container(content=self.speed_meter, bottom=10, left=10),
                                ft.Container(content=self.power_meter, top=10),
                                ft.Container(content=self.torque_meter, bottom=10, right=10)
                            ])
                    )
                ])
        except:
            logging.exception('exception occured at DualMeters.build')


    def reload(self):
        try:
            if self.power_meter:
                self.power_meter.reload()

            if self.torque_meter:    
                self.torque_meter.reload()

            if self.speed_meter:    
                self.speed_meter.reload()
            
            if self.thrust_meter:
                self.thrust_meter.reload()
        except:
            logging.exception('exception occured at DualMeters.reload')

