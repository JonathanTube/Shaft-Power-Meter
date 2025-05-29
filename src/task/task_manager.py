import asyncio
import flet as ft
from jm3846.JM3846_client import jm3846Client
from task.utc_timer_task import utc_timer
from task.sps1_read_task import Sps1ReadTask
from task.sps2_read_task import Sps2ReadTask
from task.gps_sync_task import GpsSyncTask


class TaskManager:
    def __init__(self, page: ft.Page):
        self.page = page

    def start_all(self):
        asyncio.create_task(utc_timer.start())
        asyncio.create_task(jm3846Client.start())
        # asyncio.create_task(Sps1ReadTask(self.page).start())
        # asyncio.create_task(Sps2ReadTask(self.page).start())
        # asyncio.create_task(GpsSyncTask(self.page).start())
