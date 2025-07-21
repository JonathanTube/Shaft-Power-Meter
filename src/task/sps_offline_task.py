import asyncio
import logging

from common.global_data import gdata
from utils.data_saver import DataSaver


class SpsOfflineTask:
    def __init__(self) -> None:
        self.task_running = True

    async def start(self):
        while self.task_running:
            try:
                if not gdata.test_mode_running:

                    if gdata.sps_offline:
                        DataSaver.save('sps', gdata.sps_offline_torque, gdata.sps_offline_thrust, gdata.sps_offline_speed)

                    if gdata.sps2_offline and gdata.amount_of_propeller == 2:
                        DataSaver.save('sps2', gdata.sps_offline_torque, gdata.sps_offline_thrust, gdata.sps_offline_speed)
            except:
                logging.exception("excpetion occured at SpsOfflineTask.start")
            finally:
                await asyncio.sleep(2)


    def stop(self):
        self.task_running = False

sps_offline_task = SpsOfflineTask()
