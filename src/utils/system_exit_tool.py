import asyncio
import sys
import flet as ft
import logging
import os
from task.sps_read_task import sps_read_task
from task.sps2_read_task import sps2_read_task
from ui.common.toast import Toast
from websocket.websocket_slave import ws_client
from websocket.websocket_master import ws_server
from task.plc_sync_task import plc
from task.gps_sync_task import gps
from task.modbus_output_task import modbus_output
from task.data_record_task import data_record_task
from task.test_mode_task import test_mode_task
from task.utc_timer_task import utc_timer
from db.models.user import User
from common.global_data import gdata


class SystemExitTool:
    @staticmethod
    def _safe_schedule_stop(coro):
        try:
            if asyncio.iscoroutine(coro):
                # 将 stop 协程调度到当前运行 loop（不 await）
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(coro)
                except RuntimeError:
                    # 没有运行 loop（防御），直接创建任务（也许会绑定默认 loop）
                    asyncio.create_task(coro)
            else:
                # 可能是同步 stop
                pass
        except Exception:
            logging.exception("_safe_schedule_stop failed")

    @staticmethod
    async def exit_app(page: ft.Page | None, user: User):
        if page is None:
            return

        try:

            msg = page.session.get("lang.toast.system_exit")
            Toast.show_success(page, msg, 1000 * 10)

            try:
                await asyncio.sleep(1)
            except:
                pass

            if gdata.configCommon.is_master:
                # 关闭sps
                SystemExitTool._safe_schedule_stop(sps_read_task.close())
                # 如果是dual才关闭
                if gdata.configCommon.is_twins:
                    SystemExitTool._safe_schedule_stop(sps2_read_task.close())

                # 关闭websocket
                SystemExitTool._safe_schedule_stop(ws_server.stop())

                # 关闭PLC
                SystemExitTool._safe_schedule_stop(plc.close())

            else:
                # 关闭websocket
                SystemExitTool._safe_schedule_stop(ws_client.stop())

            # 关闭GPS
            SystemExitTool._safe_schedule_stop(gps.close())

            # 关闭modbus
            SystemExitTool._safe_schedule_stop(modbus_output.stop())

            # 关闭sps_offline
            SystemExitTool._safe_schedule_stop(data_record_task.stop())

            # 关闭时间task
            SystemExitTool._safe_schedule_stop(utc_timer.stop())

            # 关闭test mode
            SystemExitTool._safe_schedule_stop(test_mode_task.stop())

            logging.info('关闭所有外部资源连接')
        except:
            logging.exception('exception occured at Header.__exit_app')
        finally:
            try:
                page.window.destroy()
            except:
                os._exit(0)  # 兜底强杀

            try:
                sys.exit(0)
            except:
                pass
