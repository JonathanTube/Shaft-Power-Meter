import asyncio

from common.global_data import gdata
from utils.data_saver import DataSaver


class SpsOfflineTask:
    async def start(self):
        while True:
            if gdata.sps1_offline:
                DataSaver.save('sps1', 0, gdata.sps_offline_torque, 0, gdata.sps_offline_thrust, gdata.sps_offline_speed)

            if gdata.sps2_offline:
                DataSaver.save('sps1', 0, gdata.sps_offline_torque, 0, gdata.sps_offline_thrust, gdata.sps_offline_speed)

            await asyncio.sleep(2)


sps_offline_task = SpsOfflineTask()