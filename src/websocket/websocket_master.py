import asyncio
import logging
import msgpack
import websockets
from common.const_alarm_type import AlarmType
from utils.alarm_saver import AlarmSaver
from task.plc_sync_task import plc


class WebSocketMaster:
    def __init__(self):
        self.client = None
        self.server = None
        self.is_online = False          # Master 是否已成功监听
        self.is_canceled = False
        self._task = None

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
        self.server = None
        self.client = None
        self.set_offline()
        logging.warning("[Master] 客户端已断开")
        AlarmSaver.create(AlarmType.SLAVE_MASTER, True)

    async def _run(self):
        """启动循环，自动重试监听"""
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
        """启动 WebSocket 服务器"""
        host, port = "0.0.0.0", 8001
        logging.info(f"[Master] 启动 ws://{host}:{port}")
        try:
            self.server = await websockets.serve(self._client_handler, host, port)
            self.set_online()
        except Exception as e:
            logging.error(f"[Master] 监听失败: {e}")
            self.set_offline()
            raise

    async def _client_handler(self, ws):
        """处理唯一客户端连接"""
        self.client = ws
        logging.info("[Master] 客户端已连接")
        AlarmSaver.recovery(AlarmType.SLAVE_MASTER)
        try:
            async for msg in ws:
                # 接收eexi breach alarm 写入plc
                occured: bool = msgpack.unpackb(msg, raw=False)
                await plc.write_eexi_breach_alarm(occured)
        except websockets.exceptions.ConnectionClosed:
            logging.info("[Master] 客户端断开")
        except Exception:
            logging.exception("[Master] 客户端异常断开")
        finally:
            self.client = None
            self.set_client_offline()

    async def send(self, data) -> bool:
        """向客户端发送数据"""
        if self.is_online and self.client:
            await self.client.send(msgpack.packb(data))
            return True
        return False

    # ===== 状态维护 =====
    def set_online(self):
        self.is_online = True
        logging.info("[Master] 监听已启动")
        AlarmSaver.recovery(AlarmType.MASTER_SERVER)

    def set_offline(self):
        self.is_online = False
        logging.warning("[Master] 监听已停止")
        AlarmSaver.create(AlarmType.MASTER_SERVER, True)


ws_server = WebSocketMaster()
