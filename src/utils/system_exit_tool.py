import flet as ft
import logging
from task.sps_read_task import sps_read_task
from task.sps2_read_task import sps2_read_task
from websocket.websocket_slave import ws_client
from websocket.websocket_master import ws_server
from task.plc_sync_task import plc
from task.gps_sync_task import gps
from task.modbus_output_task import modbus_output
from task.sps_offline_task import sps_offline_task
from task.test_mode_task import test_mode_task
from task.utc_timer_task import utc_timer
from db.models.user import User
from common.operation_type import OperationType
from db.models.operation_log import OperationLog
from common.global_data import gdata


class SystemExitTool:
    @staticmethod
    async def exit_app(page: ft.Page | None, user: User):
        if page is None:
            return

        try:
            user_id = user.id
            OperationLog.create(
                user_id=user_id,
                utc_date_time=gdata.utc_date_time,
                operation_type=OperationType.SYSTEM_EXIT,
                operation_content=user.user_name
            )

            logging.info('start closing all of the connections...')
            # 关闭sps
            await sps_read_task.close()
            await sps2_read_task.close()

            # 关闭websocket
            await ws_server.stop()
            await ws_client.close()

            # 关闭PLC
            await plc.close()

            # 关闭GPS
            await gps.close()

            # 关闭modbus
            await modbus_output.stop()

            # 关闭sps_offline
            sps_offline_task.stop()

            # 关闭test mode
            test_mode_task.stop()

            # 关闭时间task
            utc_timer.stop()

            logging.info('all of the connections were closed.')
        except:
            logging.exception('exception occured at Header.__exit_app')
        finally:
            page.window.destroy()
