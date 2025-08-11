import asyncio
import logging
import msgpack
import websockets
from typing import Set
from peewee import fn
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from db.models.io_conf import IOConf
from utils.alarm_saver import AlarmSaver
from common.global_data import gdata
from task.plc_sync_task import plc
from utils.datetime_util import DateTimeUtil

_logger = logging.getLogger("WebSocketMaster")


class WebSocketMaster:
    def __init__(self):
        # 异步锁，保证启动/重启/关闭时的线程安全
        self._lock = asyncio.Lock()

        # 已连接客户端集合（WebSocketServerProtocol）
        self.clients: Set[websockets.WebSocketServerProtocol] = set()

        # websockets.server.Serve 对象
        self.server = None

        # 表示 Master 服务总体是否在线（至少 server 已运行）
        self.is_online = False

        # 表示是否有客户端在线（任何一个客户端连接）
        self.is_client_online = False

        # 主运行任务引用（后台任务）
        self._task: asyncio.Task | None = None

    async def start(self):
        """启动 WebSocket 服务（非阻塞，返回后台 Task）"""
        # 如果任务已经存在且运行中，直接返回
        if self._task and not self._task.done():
            return self._task

        # 创建后台主循环任务
        self._task = asyncio.create_task(self._run(), name="websocket-server-task")
        return self._task

    async def stop(self):
        """停止 WebSocket 服务"""
        logging.info("[Master服务端] 正在停止")

        if self.server:
            try:
                self.server.close()
                logging.info("[Master服务端] WebSocket 服务关闭信号已发送")
            except Exception:
                logging.exception("[Master服务端] 关闭 server 时出错")

        if self._task:
            self._task.cancel()  # 只取消，不 await，避免跨事件循环
            self._task = None

        self.server = None
        self.set_offline()
        self.set_client_offline()


    async def _close_client(self, websocket):
        try:
            await websocket.close()
        except Exception:
            pass
        finally:
            if websocket in self.clients:
                try:
                    self.clients.remove(websocket)
                except Exception:
                    pass

    async def _run(self):
        """主循环：启动服务并保持运行，发生异常后自动重启（无限重试）"""
        while True:
            try:
                await self._start_server()
                self.set_online()
                # 等待 server 关闭（如果被 stop() 调用关闭，会返回）
                await self.server.wait_closed()
                _logger.info("[Master服务端] server.wait_closed 返回，准备重启或退出")
            except asyncio.CancelledError:
                _logger.info("[Master服务端] 后台任务被取消，退出主循环")
                break
            except Exception:
                _logger.exception("[Master服务端] 运行异常，3秒后重试启动")
                self.set_offline()
            finally:
                # 清理当前 clients 列表（server 关闭时，客户端也会断开）
                # 这里不强制关闭 db 操作等，保证快速循环
                await asyncio.sleep(3)

    async def _start_server(self):
        """启动 websockets server（在锁里面保证不会并发启动）"""
        async with self._lock:
            # 从数据库读取配置（在线程池中执行以免阻塞事件循环）
            try:
                io_conf = await asyncio.to_thread(IOConf.get)
            except Exception as e:
                _logger.exception(f"[Master服务端] 读取 IOConf 失败: {e}")
                raise

            host = "0.0.0.0"
            port = io_conf.hmi_server_port
            _logger.info(f"[Master服务端] 正在启动 WebSocket 服务 ws://{host}:{port}")

            # 启动并保存 Serve 对象
            try:
                self.server = await websockets.serve(
                    self._client_handler,
                    host,
                    port,
                    ping_interval=30,
                    ping_timeout=10,
                )
                _logger.info(f"[Master服务端] WebSocket 服务启动成功 ws://{host}:{port}")
            except Exception:
                _logger.exception("[Master服务端] 启动 WebSocket 服务失败")
                raise

    async def _client_handler(self, websocket: websockets.WebSocketServerProtocol):
        """单个客户端连接处理：并行执行消息监听与 ping 两个任务"""
        # 添加到客户端集合
        self.clients.add(websocket)
        # 有客户端时设置 client_online
        self.set_client_online()

        try:
            # 并行运行 consumer + ping
            consumer_task = asyncio.create_task(self._listen_client_messages(websocket))
            ping_task = asyncio.create_task(self._ping_client(websocket))

            # 等待任一任务结束（通常是连接关闭或异常）
            done, pending = await asyncio.wait(
                [consumer_task, ping_task], return_when=asyncio.FIRST_EXCEPTION
            )

            # 取消未完成的任务
            for t in pending:
                t.cancel()
                try:
                    await t
                except asyncio.CancelledError:
                    pass
                except Exception:
                    _logger.exception("[Master服务端] 取消客户端子任务时出错")

        except asyncio.CancelledError:
            # 被外部取消（服务停止）
            pass
        except websockets.exceptions.ConnectionClosed:
            # 客户端主动关闭
            pass
        except Exception:
            _logger.exception("[Master服务端] 客户端处理异常")
        finally:
            # 客户断开后从集合移除并更新状态
            try:
                if websocket in self.clients:
                    self.clients.remove(websocket)
            except Exception:
                pass

            if self.clients:
                # 还有其它客户端在线
                self.set_client_online()
            else:
                # 无客户端在线，标记离线
                self.set_client_offline()

    async def _ping_client(self, websocket: websockets.WebSocketServerProtocol):
        """定期向客户端发送 ping 心跳，检测连接活性"""
        try:
            while True:
                await asyncio.sleep(30)
                try:
                    await websocket.ping()
                except Exception:
                    # ping 失败则退出，交由外层处理移除
                    break
        except asyncio.CancelledError:
            pass

    async def _listen_client_messages(self, websocket: websockets.WebSocketServerProtocol):
        """监听客户端消息，并分发处理"""
        try:
            async for message in websocket:
                # 在接收到的每条消息上运行处理器
                await self._process_slave_message(message)
        except websockets.exceptions.ConnectionClosed:
            _logger.info("[Master服务端] 客户端连接已关闭")
        except Exception as e:
            _logger.exception(f"[Master服务端] 处理客户端消息异常: {e}")

    async def _process_slave_message(self, message: bytes):
        """处理从客户端接收的消息（解包并分发）"""
        try:
            data = msgpack.unpackb(message, raw=False)
            msg_type = data.get("type")

            if msg_type == "alarm_logs_from_slave":
                await self._sync_alarm_logs_from_slave(data.get("data", []))
            elif msg_type == "alarm_eexi_breach":
                await self._sync_alarm_eexi_breach_from_slave(data.get("data", False))
            else:
                _logger.warning(f"[Master服务端] 未知消息类型: {msg_type}")
        except Exception as e:
            _logger.exception(f"[Master服务端] 消息解析失败: {e}")

    async def _sync_alarm_eexi_breach_from_slave(self, occured):
        """收到 slave 的 eexi breach 报警后写入 PLC（或其他处理）"""
        try:
            await plc.write_eexi_breach_alarm(occured)
        except Exception:
            _logger.exception("[Master服务端] 写入 PLC eexi 报警失败")

    async def _sync_alarm_logs_from_slave(self, alarm_logs: list):
        """把从 slave 接收的报警日志同步到数据库（使用线程池操作 DB）"""
        if not alarm_logs:
            return

        try:
            # 为避免阻塞事件循环，把 DB 操作放到线程池
            await asyncio.to_thread(self._sync_alarm_logs_blocking, alarm_logs)
            _logger.info(f"[Master服务端] 已同步 {len(alarm_logs)} 条来自 slave 的报警日志")
        except Exception:
            _logger.exception("[Master服务端] 同步来自 slave 的报警日志失败")

    def _sync_alarm_logs_blocking(self, alarm_logs: list):
        """在线程池中实际执行的阻塞性 DB 操作"""
        try:
            for alarm_log in alarm_logs:
                outer_id = alarm_log["id"]
                alarm_type = alarm_log["alarm_type"]
                occured_time = alarm_log["occured_time"]
                recovery_time = alarm_log["recovery_time"]
                acknowledge_time = alarm_log["acknowledge_time"]

                cnt: int = AlarmLog.select(fn.COUNT(AlarmLog.id)).where(AlarmLog.outer_id == outer_id).scalar()

                if cnt > 0:
                    AlarmLog.update(
                        recovery_time=DateTimeUtil.parse_date(recovery_time),
                        acknowledge_time=DateTimeUtil.parse_date(acknowledge_time)
                    ).where(AlarmLog.outer_id == outer_id).execute()
                else:
                    AlarmLog.create(
                        alarm_type=alarm_type,
                        occured_time=DateTimeUtil.parse_date(occured_time),
                        recovery_time=DateTimeUtil.parse_date(recovery_time),
                        acknowledge_time=DateTimeUtil.parse_date(acknowledge_time),
                        is_from_master=False,
                        outer_id=outer_id
                    )
        except Exception:
            # 这里在线程池中，捕获并向上抛异常由调用者记录
            raise

    async def broadcast(self, data) -> bool:
        """向所有已连接客户端广播数据（非阻塞）"""
        if not self.is_online or not self.clients:
            return False

        try:
            packed_data = msgpack.packb(data)
            # gather 发送，如果某个 client 抛错会被捕获
            await asyncio.gather(*[client.send(packed_data) for client in list(self.clients)])
            return True
        except (websockets.ConnectionClosedError,
                websockets.ConnectionClosedOK,
                websockets.ConnectionClosed):
            _logger.error("[Master服务端] 广播失败：有客户端连接已关闭")
        except Exception:
            _logger.exception("[Master服务端] 广播到所有客户端失败")
        return False

    # ---- 状态管理 ----
    def set_online(self):
        """标记 Master 服务在线（server 已启动）"""
        if not self.is_online:
            self.is_online = True
            # 从 master 角度恢复告警
            AlarmSaver.recovery(AlarmType.MASTER_SERVER)

    def set_offline(self):
        """标记 Master 服务离线（server 未运行）"""
        if self.is_online:
            self.is_online = False
            AlarmSaver.create(AlarmType.MASTER_SERVER)

    def set_client_online(self):
        """标记至少有一个客户端在线"""
        if not self.is_client_online:
            self.is_client_online = True
            AlarmSaver.recovery(AlarmType.SLAVE_MASTER)

    def set_client_offline(self):
        """标记无客户端在线"""
        if self.is_client_online:
            self.is_client_online = False
            AlarmSaver.create(AlarmType.SLAVE_MASTER)


# 全局单例
ws_server = WebSocketMaster()
