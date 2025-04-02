import flet as ft


from .manually import CounterManually
from .interval import CounterInterval
from .total import CounterTotal


class Counter(ft.Container):
    def __init__(self, dual: bool = False):
        super().__init__()
        self.dual = dual
        self.padding = 10
        self.expand = True

    def build(self):
        if self.dual:
            self.content = ft.Column(
                expand=True,
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
            self.content = ft.Row(
                scroll=ft.ScrollMode.ADAPTIVE,
                controls=[
                    CounterInterval('SPS1'),
                    CounterManually('SPS1'),
                    CounterTotal('SPS1')
                ])
