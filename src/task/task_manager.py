import asyncio
import logging
import flet as ft
from db.models.io_conf import IOConf
from db.models.system_settings import SystemSettings
from task.utc_timer_task import UtcTimer
from task.sps1_read_task import sps1_read_task
from task.sps2_read_task import sps2_read_task
from websocket.websocket_server import ws_server
from websocket.websocket_client import ws_client


class TaskManager:
    def __init__(self, page: ft.Page):
        self.page = page
        self.io_conf: IOConf = IOConf.get()
        system_settings: SystemSettings = SystemSettings.get()
        self.amount_of_propeller = system_settings.amount_of_propeller

    def start_all(self):
        asyncio.create_task(UtcTimer().start())

        if self.io_conf.connect_to_sps:
            asyncio.create_task(sps1_read_task.start())
            # start sps2 JM3846 if dual propellers.
            if self.amount_of_propeller > 1:
                asyncio.create_task(sps2_read_task.start())
            asyncio.create_task(ws_server.start())
            logging.info('This HMI is configured to connect to SPS, starting JM3846 client and websocket server.')
        else:
            logging.info('This HMI is not configured to connect to SPS, starting websocket client.')
            asyncio.create_task(ws_client.connect())
            
       
        # asyncio.create_task(GpsSyncTask(self.page).start())
