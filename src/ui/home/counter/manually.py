import flet as ft
from typing import Literal
from datetime import datetime

from ui.common.simple_card import SimpleCard
from .display import CounterDisplay


class CounterManually(ft.Container):
    def __init__(self, name: Literal['SPS1', 'SPS2']):
        super().__init__()
        self.expand = True
        self.name = name
        self.start_time = None
        self.stop_time = None
        self.status: Literal['stopped', 'running', 'Reset'] = 'stopped'

    def __on_start(self, e):
        print("start")
        self.start_time = datetime.now()
        self.start_button.visible = False
        self.stop_button.visible = True
        self.resume_button.visible = False
        self.status_text.value = 'Running'
        self.status_text.color = ft.Colors.GREEN
        self.status = 'running'
        self.content.update()

    def __on_stop(self, e):
        self.stop_time = datetime.now()
        self.start_button.visible = False
        self.stop_button.visible = False
        self.resume_button.visible = True
        self.status_text.value = 'Reset'
        self.status_text.color = ft.Colors.RED
        self.status = 'reset'
        self.content.update()

    def __on_resume(self, e):
        self.start_time = datetime.now()
        self.start_button.visible = True
        self.stop_button.visible = False
        self.resume_button.visible = False
        self.status_text.value = 'Stopped'
        self.status_text.color = ft.Colors.ORANGE
        self.status = 'stopped'
        self.content.update()

    def build(self):
        display = CounterDisplay()

        stopped_at = ft.Text("Stopped", weight=ft.FontWeight.BOLD,
                             color=ft.Colors.RED_500)
        time_elapsed = ft.Text("00 d 23:10:01 h measured")
        stopped_at = ft.Text("stopped at 18/07/2014 06:56:19")

        self.status_text = ft.Text(
            self.status, size=18, weight=ft.FontWeight.BOLD)

        self.start_button = ft.FilledButton(
            text="Start",
            bgcolor=ft.Colors.GREEN,
            width=220   ,
            visible=self.status == 'stopped',
            on_click=lambda e: self.__on_start(e)
        )

        self.stop_button = ft.FilledButton(
            text="Stop",
            bgcolor=ft.Colors.RED,
            width=220,
            visible=self.status == 'running',
            on_click=lambda e: self.__on_stop(e)
        )

        self.resume_button = ft.FilledButton(
            text="Resume",
            bgcolor=ft.Colors.ORANGE,
            width=220,
            visible=self.status == 'reset',
            on_click=lambda e: self.__on_resume(e)
        )

        self.content = SimpleCard(
            title="Manually",
            expand=False,
            body=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    display,
                    self.status_text,
                    # stopped_at,
                    # time_elapsed,
                    self.start_button,
                    self.stop_button,
                    self.resume_button
                ]
            )
        )
