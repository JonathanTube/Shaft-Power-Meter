import asyncio
from db.models.system_settings import SystemSettings
from task.gps_sync_task import gps_sync_task
from task.sps_offline_task import sps_offline_task
from task.utc_timer_task import UtcTimer
from task.sps1_read_task import sps1_read_task
from task.sps2_read_task import sps2_read_task
from utils.plc_util import plc_util
from websocket.websocket_server import ws_server
from websocket.websocket_client import ws_client


class TaskManager:
    def __init__(self):
        self.system_settings: SystemSettings = SystemSettings.get()

    def start_all(self, is_db_empty : bool):            
        asyncio.create_task(UtcTimer().start())

        asyncio.create_task(sps_offline_task.start())

        # 如果是第一次装机，不启动其他设备连接
        if is_db_empty:
            return

        asyncio.create_task(gps_sync_task.start())

        asyncio.create_task(plc_util.auto_reconnect())

        if not self.system_settings.is_master:
            asyncio.create_task(ws_client.connect())
            return
        

        asyncio.create_task(sps1_read_task.start())

        # start sps2 JM3846 if dual propellers.
        if self.system_settings.amount_of_propeller > 1:
            asyncio.create_task(sps2_read_task.start())

        asyncio.create_task(ws_server.start())

