import asyncio
import flet as ft
from task.utc_timer_task import utc_timer
from task.counter_total_task import CounterTotalTask
from task.counter_manually_task import CounterManuallyTask
from task.counter_interval_task import CounterIntervalTask
from task.plc_sync_task import PlcSyncTask
from task.modbus_read_task import ModbusReadTask
from task.data_save_task import DataSaveTask
from task.gps_read_task import GpsReadTask
from task.eexi_breach_task import EEXIBreachTask
from task.power_overload_task import PowerOverloadTask


class TaskManager:
    def __init__(self, page: ft.Page):
        self.page = page

    def start_all(self):
        asyncio.create_task(utc_timer.start())
        asyncio.create_task(CounterTotalTask(self.page).start())
        asyncio.create_task(CounterManuallyTask(self.page).start())
        asyncio.create_task(CounterIntervalTask(self.page).start())

        asyncio.create_task(PlcSyncTask(self.page).start())
        asyncio.create_task(ModbusReadTask(self.page).start())
        asyncio.create_task(DataSaveTask(self.page).start())
        asyncio.create_task(GpsReadTask(self.page).start())

        asyncio.create_task(EEXIBreachTask(self.page).start())
        asyncio.create_task(PowerOverloadTask(self.page).start())
