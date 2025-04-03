import flet as ft

from db.models.system_settings import SystemSettings
from ui.home.dashboard.sps_single.off.index import SingleShaPoLiOff
from ui.home.dashboard.sps_single.on.index import SingleShaPoLiOn
from .manually import CounterManually
from .interval import CounterInterval
from .total import CounterTotal


class Counter(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 10
        self.expand = True

        self.__load_config()

    def __load_config(self):
        system_settings: SystemSettings = SystemSettings.get_or_none()
        self.dual = system_settings.amount_of_propeller == 2

    def build(self):
        if self.dual:
            self.content = ft.Column(
                controls=[
                    ft.Text('SPS1', weight=ft.FontWeight.BOLD, size=16),
                    ft.Row(
                        expand=True,
                        controls=[
                            CounterInterval('SPS1'),
                            CounterManually('SPS1'),
                            CounterTotal('SPS1')
                        ]),
                    ft.Text('SPS2', weight=ft.FontWeight.BOLD, size=16),
                    ft.Row(
                        expand=True,
                        controls=[
                            CounterInterval('SPS2'),
                            CounterManually('SPS2'),
                            CounterTotal('SPS2')
                        ])
                ]
            )
        else:
            self.content = ft.Column(
                controls=[
                    ft.Row(
                        expand=True,
                        controls=[
                            CounterInterval('SPS1'),
                            CounterManually('SPS1'),
                            CounterTotal('SPS1')
                        ]
                    ),
                    ft.Text('', expand=True)
                ]
            )
