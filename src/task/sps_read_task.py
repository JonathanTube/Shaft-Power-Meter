import asyncio
from jm3846.JM3846_client import JM3846AsyncClient
from jm3846.JM3846_torque_rpm import jm3846_torque_rpm
from jm3846.JM3846_thrust import jm3846_thrust
from db.models.io_conf import IOConf
from common.global_data import gdata
from common.const_alarm_type import AlarmType
from utils.alarm_saver import AlarmSaver


class SpsReadTask(JM3846AsyncClient):
    def __init__(self):
        super().__init__("sps")

    def get_ip_port(self) -> tuple[str, int]:
        io_conf: IOConf = IOConf.get()
        return io_conf.sps_ip, io_conf.sps_port

    def set_offline_hook(self, is_offline: bool):
        gdata.configSPS.is_offline = is_offline

    def create_alarm_hook(self):
        AlarmSaver.create(alarm_type=AlarmType.MASTER_SPS_DISCONNECTED)

    def recovery_alarm_hook(self):
        AlarmSaver.recovery(
            alarm_type_occured=AlarmType.MASTER_SPS_DISCONNECTED,
            alarm_type_recovered=AlarmType.MASTER_SPS_CONNECTED
        )

    def start_background_tasks(self):
        if not jm3846_torque_rpm.is_running():
            self._bg_tasks.append(asyncio.create_task(jm3846_torque_rpm.start(self.name)))
        if not jm3846_thrust.is_running():
            self._bg_tasks.append(asyncio.create_task(jm3846_thrust.start(self.name)))

    def stop_background_tasks(self):
        jm3846_torque_rpm.stop()
        jm3846_thrust.stop()
        for t in self._bg_tasks:
            if not t.done():
                t.cancel()
        self._bg_tasks.clear()


sps_read_task = SpsReadTask()
