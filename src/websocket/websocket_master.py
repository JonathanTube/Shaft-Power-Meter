import asyncio
from datetime import datetime
import logging
import msgpack
import websockets
from typing import Set
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from db.models.io_conf import IOConf
from utils.alarm_saver import AlarmSaver
from common.global_data import gdata
from task.plc_sync_task import plc

date_time_format = '%Y-%m-%d %H:%M:%S'


class WebSocketMaster:
    def __init__(self):
        self._lock = asyncio.Lock()  # 线程安全锁
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.server = None

        self._max_retries = 6  # 最大重连次数

        self._is_started = False
        self._is_canceled = False

    @property
    def is_started(self):
        return self._is_started

    async def _client_handler(self, websocket):
        self.clients.add(websocket)
        try:
            while gdata.configCommon.is_master:
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
                    AlarmSaver.recovery(AlarmType.MASTER_SERVER)

                    asyncio.create_task(self.receive_alarms_from_slave())

                    await self.send_alarms_to_salve()

                except:
                    logging.exception('exception occured at WebSocketServer.start')
                    self._is_started = False
                    AlarmSaver.create(AlarmType.MASTER_SERVER)
                finally:
                    #  指数退避
                    await asyncio.sleep(2 ** attempt)

            # 执行到这了，说明已经退出了
            self._is_canceled = False

    async def send_alarms_to_salve(self):
        """主机向从机发送未同步的alarm"""
        while gdata.configCommon.is_master and self._is_started:

            if self._is_canceled:
                return

            try:
                if len(self.clients) > 0:
                    AlarmSaver.recovery(AlarmType.SLAVE_CLIENT)

                    alarm_logs: list[AlarmLog] = AlarmLog.select(
                        AlarmLog.id,
                        AlarmLog.alarm_type,
                        AlarmLog.is_recovery,
                        AlarmLog.utc_date_time,
                        AlarmLog.acknowledge_time
                    ).where(
                        AlarmLog.is_sync == False,
                        AlarmLog.is_from_master == True,
                        # 彼此的连接错误不同步
                        AlarmLog.alarm_type != AlarmType.SLAVE_CLIENT
                    )

                    alarm_logs_dict = []
                    for alarm_log in alarm_logs:
                        alarm_logs_dict.append({
                            'id': alarm_log.id,
                            'alarm_type': alarm_log.alarm_type,
                            'is_recovery': 1 if alarm_log.is_recovery else 0,
                            'utc_date_time': alarm_log.utc_date_time.strftime(date_time_format) if alarm_log.utc_date_time else "",
                            'acknowledge_time': alarm_log.acknowledge_time.strftime(date_time_format) if alarm_log.acknowledge_time else ""
                        })
                    if len(alarm_logs) > 0:
                        is_success = await self.broadcast({'type': 'alarm_logs_from_master', 'data': alarm_logs_dict})
                        if is_success:
                            for alarm_log in alarm_logs:
                                AlarmLog.update(is_sync=True).where(AlarmLog.id == alarm_log.id).execute()

                else:
                    AlarmSaver.create(AlarmType.SLAVE_CLIENT)
            except websockets.ConnectionClosedError:
                logging.exception("[***HMI server***] broadcast to all clients,ConnectionClosedError occured")
            except:
                logging.exception("[***HMI server***] exception occured at send_alarms")
            finally:
                try:
                    await asyncio.sleep(5)
                except:
                    pass

    async def receive_alarms_from_slave(self):
        """接收从客户端（slave）发送的报警消息"""
        while gdata.configCommon.is_master and self._is_started:
            if self._is_canceled:
                return

            try:
                # 为每个客户端创建独立的消息监听任务
                tasks = [self._listen_client_messages(client) for client in list(self.clients)]
                if tasks:
                    await asyncio.gather(*tasks)
            except Exception as e:
                logging.exception(f"[***HMI server***] 接收消息异常: {e}")
            finally:
                await asyncio.sleep(5)  # 避免空循环占用资源

    async def _listen_client_messages(self, websocket: websockets.WebSocketServerProtocol):
        """监听单个客户端的消息流"""
        try:
            async for message in websocket:
                await self._process_slave_message(message)
        except websockets.exceptions.ConnectionClosed:
            logging.info("[***HMI server***] 客户端连接已关闭")
        except Exception as e:
            logging.exception(f"[***HMI server***] 处理消息异常: {e}")

    async def _process_slave_message(self, message: bytes):
        """处理从客户端接收的消息"""
        try:
            data = msgpack.unpackb(message, raw=False)
            msg_type = data.get('type')

            if msg_type == 'alarm_logs_from_slave':
                await self._sync_alarm_logs_from_slave(data.get('data', []))
            if msg_type == 'alarm_eexi_breach':
                await self._sync_alarm_eexi_breach_from_slave(data.get('data', False))
            else:
                logging.warning(f"未知消息类型: {msg_type}")
        except Exception as e:
            logging.exception(f"消息解析失败: {e}")

    async def _sync_alarm_eexi_breach_from_slave(self, occured):
        """同步来自slave的eexi breach报警"""
        await plc.write_eexi_breach_alarm(occured)

    async def _sync_alarm_logs_from_slave(self, alarm_logs: list):
        """将从客户端接收的报警日志同步到数据库"""
        if not alarm_logs:
            return

        try:
            for alarm_log in alarm_logs:
                outer_id = alarm_log['id']
                alarm_type = alarm_log['alarm_type']
                is_recovery = alarm_log['is_recovery']
                utc_date_time = alarm_log['utc_date_time']
                acknowledge_time = alarm_log['acknowledge_time']

                ack_time = None
                if acknowledge_time:
                    ack_time = datetime.strptime(acknowledge_time, date_time_format)

                udt = None
                if utc_date_time:
                    udt = datetime.strptime(utc_date_time, date_time_format)

                cnt: int = AlarmLog.select().where(AlarmLog.outer_id == outer_id).count()

                if cnt > 0:
                    AlarmLog.update(acknowledge_time=ack_time).where(AlarmLog.outer_id == outer_id).execute()
                else:
                    AlarmLog.create(
                        utc_date_time=udt, acknowledge_time=ack_time,
                        alarm_type=alarm_type, is_recovery=is_recovery,
                        is_from_master=False, outer_id=outer_id
                    )

            logging.info(f"成功同步 {len(alarm_logs)} 条报警slave GPS报警日志")
        except Exception as e:
            logging.exception(f"数据库同步失败: {e}")

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


ws_server = WebSocketMaster()
