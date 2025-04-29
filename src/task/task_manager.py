import asyncio
import flet as ft
from task.utc_timer_task import utc_timer
from task.plc_sync_task import PlcSyncTask
from task.sps1_read_task import Sps1ReadTask
from task.sps2_read_task import Sps2ReadTask
from task.gps_sync_task import GpsSyncTask


class TaskManager:
    def __init__(self, page: ft.Page):
        self.page = page

    def start_all(self):
        asyncio.create_task(utc_timer.start())

        # asyncio.create_task(PlcSyncTask(self.page).start())
        # asyncio.create_task(Sps1ReadTask(self.page).start())
        # asyncio.create_task(Sps2ReadTask(self.page).start())
        # asyncio.create_task(GpsSyncTask(self.page).start())
