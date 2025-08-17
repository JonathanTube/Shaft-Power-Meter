import asyncio
import logging
import msgpack
import websockets
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from utils.alarm_saver import AlarmSaver
from task.plc_sync_task import plc
from utils.datetime_util import DateTimeUtil


class WebSocketMaster:
    def __init__(self):
        self.client = None
        self.server = None
        self.is_online = False
        self.is_canceled = False
        self._task = None
        self._periodic_task_handle = None  # 定时任务句柄

    async def start(self):
        """启动 Master 监听"""
        self.is_canceled = False
        if not self._task or self._task.done():
            self._task = asyncio.create_task(self._run())
        return self._task

    async def stop(self):
        """停止 Master 监听"""
        logging.info("[Master] 停止监听")
        self.is_canceled = True
        if self.server:
            self.server.close()
        if self.client:
            await self.client.close()
        if self._task:
            self._task.cancel()
            self._task = None
        if self._periodic_task_handle:
            self._periodic_task_handle.cancel()
            self._periodic_task_handle = None
        self.server = None
        self.client = None
        self.set_offline()

    async def _run(self):
        while not self.is_canceled:
            try:
                await self._start_server()
                await self.server.wait_closed()
                self.set_offline()
            except asyncio.CancelledError:
                break
            except Exception:
                logging.exception("[Master] 异常，3秒后重试")
                self.set_offline()
            await asyncio.sleep(3)

    async def _start_server(self):
        host, port = "0.0.0.0", 8001
        logging.info(f"[Master] 启动 ws://{host}:{port}")
        try:
            self.server = await websockets.serve(self._client_handler, host, port)
            self.set_online()
            # 启动定时任务
            self._periodic_task_handle = asyncio.create_task(self._sync_alarms_to_slave())
        except Exception as e:
            logging.error(f"[Master] 监听失败: {e}")
            self.set_offline()
            raise

    async def _client_handler(self, ws):
        self.client = ws
        logging.info("[Master] 客户端已连接")
        AlarmSaver.recovery(AlarmType.SLAVE_MASTER)
        try:
            async for msg in ws:
                res = msgpack.unpackb(msg, raw=False)
                type = res['type']
                if type == 'eexi_breach':
                    await plc.write_eexi_breach_alarm(res['data'])
                if type == 'alarm_ack':
                    self._handle_alarm_synced(res['data'])

        except websockets.exceptions.ConnectionClosed:
            logging.info("[Master] 客户端断开")
        except Exception:
            logging.exception("[Master] 客户端异常断开")
        finally:
            self.client = None

    def _handle_alarm_synced(self, alarm_uuid):
        try:
            AlarmLog.update(is_synced=True).where(AlarmLog.alarm_uuid == alarm_uuid).execute()
        except Exception as e:
            logging.exception(f"[PLC] alarm ack 失败, alarm_uuid={alarm_uuid}", e)

    async def _sync_alarms_to_slave(self):
        """每 2 秒执行一次的任务"""
        try:
            while not self.is_canceled and self.is_online:
                # 查找未同步的数据
                alarms: list[AlarmLog] = AlarmLog.select(
                    AlarmLog.alarm_uuid,
                    AlarmLog.alarm_type,
                    AlarmLog.occured_time,
                    AlarmLog.recovery_time,
                    AlarmLog.acknowledge_time
                ).where(
                    AlarmLog.out_of_sync == False,
                    AlarmLog.is_synced == False
                ).limit(100)

                arr = []
                for alarm in alarms:
                    arr.append({
                        'alarm_uuid': alarm.alarm_uuid,
                        'alarm_type': alarm.alarm_type,
                        'occured_time': DateTimeUtil.format_date(alarm.occured_time),
                        'recovery_time': DateTimeUtil.format_date(alarm.recovery_time),
                        'acknowledge_time': DateTimeUtil.format_date(alarm.acknowledge_time)
                    })

                await self.send({
                    'type': 'alarms',
                    'data': arr
                })

                await asyncio.sleep(2)
        except asyncio.CancelledError:
            pass
        except Exception:
            logging.exception("[Master] 定时任务异常")

    async def send(self, data) -> bool:
        if self.is_online and self.client:
            await self.client.send(msgpack.packb(data))
            return True
        return False

    def set_online(self):
        self.is_online = True
        logging.info("[Master] 监听已启动")
        AlarmSaver.recovery(AlarmType.MASTER_SERVER)

    def set_offline(self):
        self.is_online = False
        logging.warning("[Master] 监听已停止")
        AlarmSaver.create(AlarmType.MASTER_SERVER, True)
        AlarmSaver.create(AlarmType.SLAVE_MASTER, True)


ws_server = WebSocketMaster()
