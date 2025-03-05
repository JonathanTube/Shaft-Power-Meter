import flet as ft

from ui.home.counter.interval import createInterval


def createCounter():
    return ft.Row(
        controls=[
            createInterval(),
            createInterval(),
            createInterval()
        ])
