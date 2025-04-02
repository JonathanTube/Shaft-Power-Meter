from typing import Literal
import flet as ft
from peewee import fn

from ui.common.simple_card import SimpleCard
from .display import CounterDisplay
from db.models.data_log import DataLog


class CounterTotal(ft.Container):
    def __init__(self, name: Literal['SPS1', 'SPS2']):
        super().__init__()
        self.expand = True
        self.name = name

    def get_data(self):
        data = DataLog.select(
            fn.sum(DataLog.power), fn.sum(DataLog.revolution)
        ).where(
            DataLog.name == self.name).scalar()
        power, revolution = data

        return data

    def build(self):
        display = CounterDisplay()
        time_elapsed = ft.Text("00 d 23:10:01 h measured")
        started_at = ft.Text("started at 18/07/2014 06:56:19")

        self.content = SimpleCard(
            title="Total",
            expand=False,
            body=ft.Column(
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    display,
                    time_elapsed,
                    started_at
                ]))
