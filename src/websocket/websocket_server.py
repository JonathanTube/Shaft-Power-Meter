import asyncio
import websockets
from typing import Set
import logging
from common.const_alarm_type import AlarmType
from db.models.io_conf import IOConf
import msgpack
from utils.alarm_saver import AlarmSaver

class WebSocketServer:
    def __init__(self):
        self._lock = asyncio.Lock()  # 线程安全锁
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.server = None

        self._max_retries = 20  # 最大重连次数
        
        self._is_started = False

    @property
    def is_started(self):
        return self._is_started

    async def _client_handler(self, websocket):
        self.clients.add(websocket)

    async def start(self):
        async with self._lock:  # 确保单线程
            for attempt in range(self._max_retries):
                if self._is_started:
                    return

                try:
                    io_conf: IOConf = IOConf.get()
                    host = '0.0.0.0'
                    port = io_conf.hmi_server_port
                    self.server = await websockets.serve(self._client_handler, host, port)
                    logging.info(f"[***HMI server***] websocket server started at ws://{host}:{port}")
                    self._is_started = True
                    AlarmSaver.recovery(alarm_type=AlarmType.MASTER_SERVER_STOPPED)
                except:
                    self._is_started = False
                    AlarmSaver.create(alarm_type=AlarmType.MASTER_SERVER_STOPPED)
                finally:
                    #  指数退避
                    await asyncio.sleep(2 ** attempt)

    async def stop(self):
        try:
            if self.server:
                self.server.close()
                await self.server.wait_closed()
                logging.info('[***HMI server***] websocket server has been stopped')
        except:
            logging.error('[***HMI server***] stop websocket server failed')
        finally:
            AlarmSaver.create(alarm_type=AlarmType.MASTER_SERVER_STOPPED)
            self._is_started = False

    async def broadcast(self, data):
        if not self._is_started:
            return

        try:
            if len(self.clients) > 0:
                packed_data = msgpack.packb(data)
                await asyncio.gather(*[client.send(packed_data) for client in self.clients])
                AlarmSaver.recovery(alarm_type=AlarmType.SLAVE_DISCONNECTED)
            else:
                AlarmSaver.create(alarm_type=AlarmType.SLAVE_DISCONNECTED)
        except:
            logging.error("[***HMI server***] broadcast to all clients failed")


ws_server = WebSocketServer()
