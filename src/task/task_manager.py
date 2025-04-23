import asyncio
import flet as ft
from task.utc_timer_task import utc_timer
from task.plc_sync_task import PlcSyncTask
from task.sps_read_task import SpsReadTask
from task.gps_sync_task import GpsSyncTask
from task.eexi_breach_task import EEXIBreachTask
from task.power_overload_task import PowerOverloadTask


class TaskManager:
    def __init__(self, page: ft.Page):
        self.page = page

    def start_all(self):
        asyncio.create_task(utc_timer.start())

        asyncio.create_task(PlcSyncTask(self.page).start())
        asyncio.create_task(SpsReadTask(self.page).start())
        asyncio.create_task(GpsSyncTask(self.page).start())

        asyncio.create_task(EEXIBreachTask(self.page).start())
        asyncio.create_task(PowerOverloadTask(self.page).start())
