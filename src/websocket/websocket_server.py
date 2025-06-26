import asyncio
import logging
import msgpack
import websockets
from typing import Set
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from db.models.io_conf import IOConf
from utils.alarm_saver import AlarmSaver
from common.global_data import gdata

date_time_format = '%Y-%m-%d %H:%M:%S'

class WebSocketServer:
    def __init__(self):
        self._lock = asyncio.Lock()  # 线程安全锁
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.server = None

        self._max_retries = 20  # 最大重连次数

        self._is_started = False
        self._is_canceled = False

    @property
    def is_started(self):
        return self._is_started

    async def _client_handler(self, websocket):
        self.clients.add(websocket)
        try:
            while gdata.is_master:
                if self._is_canceled:
                    return

                # 每30秒发送一次心跳
                await asyncio.sleep(30)
                await websocket.ping()
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)

    async def start(self):
        async with self._lock:  # 确保单线程
            if self._is_started:
                return

            self._is_canceled = False

            for attempt in range(self._max_retries):
                if self._is_canceled:
                    return

                try:
                    io_conf: IOConf = IOConf.get()
                    host = '0.0.0.0'
                    port = io_conf.hmi_server_port
                    self.server = await websockets.serve(self._client_handler, host, port, ping_interval=30, ping_timeout=10)
                    logging.info(f"[***HMI server***] websocket server started at ws://{host}:{port}")
                    self._is_started = True
                    AlarmSaver.recovery(alarm_type=AlarmType.MASTER_SERVER_STOPPED)

                    await self.send_alarms()
                except:
                    logging.exception('exception occured at WebSocketServer.start')
                    self._is_started = False
                    AlarmSaver.create(alarm_type=AlarmType.MASTER_SERVER_STOPPED)
                finally:
                    #  指数退避
                    await asyncio.sleep(2 ** attempt)

            # 执行到这了，说明已经退出了
            self._is_canceled = False

    async def send_alarms(self):
        while gdata.is_master and self._is_started:

            if self._is_canceled:
                return

            try:
                if len(self.clients) > 0:
                    AlarmSaver.recovery(alarm_type=AlarmType.SLAVE_DISCONNECTED)

                    # GPS不同步
                    alarm_logs: list[AlarmLog] = AlarmLog.select(
                        AlarmLog.id,
                        AlarmLog.alarm_type,
                        AlarmLog.is_recovery,
                        AlarmLog.acknowledge_time
                    ).where(
                        AlarmLog.is_sync == False,
                        AlarmLog.alarm_type != AlarmType.GPS_DISCONNECTED
                    )
                    
                    alarm_logs_dict = []
                    for alarm_log in alarm_logs:
                        alarm_logs_dict.append({
                            'alarm_type':alarm_log.alarm_type,
                            'acknowledge_time':alarm_log.acknowledge_time.strftime(date_time_format) if alarm_log.acknowledge_time else "",
                            'is_recovery': 1 if alarm_log.is_recovery else 0
                        })
                    if len(alarm_logs) > 0:
                        is_success = await self.broadcast({'type': 'alarm_data', "alarm_logs": alarm_logs_dict})
                        if is_success:
                            for alarm_log in alarm_logs:
                                AlarmLog.update(is_sync=True).where(AlarmLog.id == alarm_log.id).execute()

                else:
                    AlarmSaver.create(alarm_type=AlarmType.SLAVE_DISCONNECTED)
            except websockets.ConnectionClosedError:
                logging.exception("[***HMI server***] broadcast to all clients,ConnectionClosedError occured")
            except:
                logging.exception("[***HMI server***] exception occured at send_alarms")
            finally:
                try:
                    await asyncio.sleep(5)
                except:
                    pass

    async def stop(self):
        self._is_canceled = True

        if not self._is_started:
            return
        
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

    async def broadcast(self, data) -> bool:
        if not self._is_started:
            return False

        if self._is_canceled:
            return False

        try:
            if len(self.clients) == 0:
                return False

            packed_data = msgpack.packb(data)
            await asyncio.gather(*[client.send(packed_data) for client in self.clients])

            return True

        except (websockets.ConnectionClosedError,
                websockets.ConnectionClosedOK,
                websockets.ConnectionClosed):
            logging.error("[***HMI server***] broadcast to all clients, connection closed")
        except:
            logging.exception("[***HMI server***] broadcast to all clients failed")

        return False


ws_server = WebSocketServer()
