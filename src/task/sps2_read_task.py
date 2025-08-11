# task/sps2_read_task.py
import logging
import asyncio
from jm3846.JM3846_client import JM3846AsyncClient
from db.models.io_conf import IOConf
from common.global_data import gdata
from common.const_alarm_type import AlarmType
from utils.alarm_saver import AlarmSaver

logger = logging.getLogger("Sps2ReadTask")


class Sps2ReadTask(JM3846AsyncClient):
    def __init__(self):
        super().__init__("sps2")

    def get_ip_port(self):
        """同步获取 SPS2 IP 和端口"""
        try:
            io_conf: IOConf = IOConf.get()
            return io_conf.sps2_ip, io_conf.sps2_port
        except Exception:
            logger.exception("[Sps2ReadTask] 获取 IO 配置失败")
            return "127.0.0.1", 502

    def set_offline_hook(self, is_offline: bool):
        """设置离线状态（非阻塞）"""
        try:
            gdata.configSPS2.is_offline = bool(is_offline)
        except Exception:
            logger.exception("[Sps2ReadTask] 设置离线状态失败")

    def create_alarm_hook(self):
        """创建报警（异步执行数据库写入）"""
        try:
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, AlarmSaver.create, AlarmType.SLAVE_SPS)
        except RuntimeError:
            # 没有事件循环时（比如同步关闭阶段），直接调用
            AlarmSaver.create(AlarmType.SLAVE_SPS)
        except Exception:
            logger.exception("[Sps2ReadTask] 创建报警失败")

    def recovery_alarm_hook(self):
        """恢复报警（异步执行数据库写入）"""
        try:
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, AlarmSaver.recovery, AlarmType.SLAVE_SPS)
        except RuntimeError:
            AlarmSaver.recovery(AlarmType.SLAVE_SPS)
        except Exception:
            logger.exception("[Sps2ReadTask] 恢复报警失败")


sps2_read_task = Sps2ReadTask()
