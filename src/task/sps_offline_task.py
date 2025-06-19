import asyncio
import logging

from common.global_data import gdata
from utils.data_saver import DataSaver


class SpsOfflineTask:
    async def start(self):
        while True:
            try:
                if not gdata.test_mode_running:

                    if gdata.sps1_offline:
                        DataSaver.save('sps1', gdata.sps_offline_torque, gdata.sps_offline_thrust, gdata.sps_offline_speed)

                    if gdata.sps2_offline and gdata.amount_of_propeller == 2:
                        DataSaver.save('sps2', gdata.sps_offline_torque, gdata.sps_offline_thrust, gdata.sps_offline_speed)
            except Exception as e:
                logging.exception(e)
            await asyncio.sleep(2)


sps_offline_task = SpsOfflineTask()