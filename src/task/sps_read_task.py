# task/sps_read_task.py
from jm3846.JM3846_client import JM3846AsyncClient
from common.const_alarm_type import AlarmType
from utils.alarm_saver import AlarmSaver
from common.global_data import gdata


class SpsReadTask(JM3846AsyncClient):
    def __init__(self):
        super().__init__("sps")
        self.is_online = None

    def get_ip_port(self):
        """同步获取 SPS IP 和端口"""
        ip = gdata.configIO.sps_ip
        port = gdata.configIO.sps_port
        return ip, port

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
