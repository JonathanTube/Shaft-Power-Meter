import asyncio
import flet as ft
from db.models.system_settings import SystemSettings
from task.utc_timer_task import UtcTimer
from task.sps1_read_task import Sps1ReadTask
from task.sps2_read_task import Sps2ReadTask


class TaskManager:
    def __init__(self, page: ft.Page):
        self.page = page

    def start_all(self):
        asyncio.create_task(UtcTimer().start())
        asyncio.create_task(Sps1ReadTask().start())

        # start sps2 JM3846 if dual propellers.
        system_settings: SystemSettings = SystemSettings.get()
        amount_of_propeller = system_settings.amount_of_propeller
        if amount_of_propeller > 1:
            asyncio.create_task(Sps2ReadTask().start())

        # asyncio.create_task(GpsSyncTask(self.page).start())
