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
                scroll=ft.ScrollMode.ADAPTIVE,
                controls=[
                    ft.Row(controls=[
                        CounterInterval("Interval(SPS1)"),
                        # CounterManually("Manually(SPS1)"),
                        # CounterTotal("Total(SPS1)")
                    ]),
                    ft.Row(controls=[
                        # CounterInterval("Interval(SPS2)"),
                        # CounterManually("Manually(SPS2)"),
                        # CounterTotal("Total(SPS2)")
                    ])
                ]
            )
        else:
            self.content = ft.Row(
                scroll=ft.ScrollMode.ADAPTIVE,
                controls=[
                    CounterInterval("Interval"),
                    CounterManually("Manually"),
                    CounterTotal("Total")
                ])
