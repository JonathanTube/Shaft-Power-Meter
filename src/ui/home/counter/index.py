import logging
import flet as ft

from db.models.system_settings import SystemSettings
from ui.home.counter.interval import IntervalCounter
from ui.home.counter.manually import ManuallyCounter
from ui.home.counter.total import TotalCounter


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
        try:
            interval_counter_sps1 = IntervalCounter('sps1')
            manually_counter_sps1 = ManuallyCounter('sps1')
            total_counter_sps1 = TotalCounter('sps1')

            if self.dual:
                interval_counter_sps2 = IntervalCounter('sps2')
                manually_counter_sps2 = ManuallyCounter('sps2')
                total_counter_sps2 = TotalCounter('sps2')

                self.content = ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        ft.Text('sps1', weight=ft.FontWeight.BOLD, size=16),
                        ft.Row(expand=True, controls=[interval_counter_sps1, manually_counter_sps1, total_counter_sps1]),
                        ft.Text('sps2', weight=ft.FontWeight.BOLD, size=16),
                        ft.Row(expand=True, controls=[interval_counter_sps2, manually_counter_sps2, total_counter_sps2])
                    ])
                return

            self.content = ft.Column(
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    ft.Row(expand=True, controls=[interval_counter_sps1, manually_counter_sps1, total_counter_sps1]),
                    ft.Text('', expand=True)
                ])
        except:
            logging.exception('exception occured at Counter.build')

