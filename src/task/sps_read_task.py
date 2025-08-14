# task/sps_read_task.py
import logging
import asyncio
from jm3846.JM3846_client import JM3846AsyncClient
from db.models.io_conf import IOConf
from common.const_alarm_type import AlarmType
from utils.alarm_saver import AlarmSaver

logger = logging.getLogger("SpsReadTask")


class SpsReadTask(JM3846AsyncClient):
    def __init__(self):
        super().__init__("sps")
        self.is_online = None

    def get_ip_port(self):
        """同步获取 SPS IP 和端口"""
        try:
            io_conf: IOConf = IOConf.get()
            return io_conf.sps_ip, io_conf.sps_port
        except Exception:
            logger.exception("[SpsReadTask] 获取 IO 配置失败")
            return "127.0.0.1", 502

    def set_online(self):
        """设置在线状态（非阻塞）"""
        if self.is_online is None or self.is_online == False:
            self.is_online = True
            AlarmSaver.recovery(AlarmType.MASTER_SPS)

    def set_offline(self):
        """设置离线状态（非阻塞）"""
        if self.is_online is None or self.is_online == True:
            self.is_online = False
            AlarmSaver.create(AlarmType.MASTER_SPS)

sps_read_task = SpsReadTask()
