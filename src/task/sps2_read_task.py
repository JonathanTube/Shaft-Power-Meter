# task/sps2_read_task.py
from jm3846.JM3846_client import JM3846AsyncClient
from common.const_alarm_type import AlarmType
from utils.alarm_saver import AlarmSaver
from common.global_data import gdata


class Sps2ReadTask(JM3846AsyncClient):
    def __init__(self):
        super().__init__("sps2")

    def get_ip_port(self):
        """同步获取 SPS2 IP 和端口"""
        ip = gdata.configIO.sps2_ip
        port = gdata.configIO.sps2_port
        return ip, port

    async def set_online(self):
        """设置在线状态（非阻塞）"""
        if self.is_online is False:
            self.is_online = True
            await AlarmSaver.recovery(AlarmType.MASTER_SPS)
        self.is_connecting = False

    async def set_offline(self):
        """设置离线状态（非阻塞）"""
        if self.is_online is True:
            self.is_online = False
            await AlarmSaver.create(AlarmType.MASTER_SPS)
        self.is_connecting = False


sps2_read_task = Sps2ReadTask()
