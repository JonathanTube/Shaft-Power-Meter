from jm3846.JM3846_client import JM3846AsyncClient
from db.models.io_conf import IOConf
from common.global_data import gdata
from common.const_alarm_type import AlarmType
from utils.alarm_saver import AlarmSaver


class Sps2ReadTask(JM3846AsyncClient):
    def __init__(self):
        super().__init__("sps2")

    def get_ip_port(self) -> tuple[str, int]:
        io_conf: IOConf = IOConf.get()
        return io_conf.sps2_ip, io_conf.sps2_port

    def set_offline_hook(self, is_offline: bool):
        gdata.configSPS2.is_offline = is_offline

    def create_alarm_hook(self):
        AlarmSaver.create(alarm_type=AlarmType.MASTER_SPS2_DISCONNECTED)

    def recovery_alarm_hook(self):
        AlarmSaver.recovery(AlarmType.MASTER_SPS2_DISCONNECTED, AlarmType.MASTER_SPS2_CONNECTED)


sps2_read_task = Sps2ReadTask()
