import flet as ft

from .interval import createInterval
from .manually import createManually
from .total import createTotal


def createCounter(dual: bool = False):
    if dual:
        return ft.Column(expand=True,
                         controls=[
                             ft.Row(controls=[
                                 createInterval("SPS1"),
                                 createManually(),
                                 createTotal()
                             ]),
                             ft.Row(controls=[
                                 createInterval("SPS2"),
                                 createManually(),
                                 createTotal()
                             ])])

    return ft.Row(controls=[
        createInterval(),
        createManually(),
        createTotal()
    ])
