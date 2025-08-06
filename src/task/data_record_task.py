import asyncio
import logging

from common.global_data import gdata
from utils.data_saver import DataSaver


class DataRecordTask:
    def __init__(self) -> None:
        self.task_running = True

    async def start(self):
        while self.task_running:
            try:
                is_dual = gdata.configCommon.amount_of_propeller == 2
                # 测试模式打开
                if gdata.configTest.test_mode_running:
                    self.save_sps_online_data()
                    if is_dual:
                        self.save_sps2_online_data()
                    continue

                # 测试模式关闭
                if gdata.configSPS.is_offline:
                    self.save_sps_offline_data()
                else:
                    self.save_sps_online_data()

                if is_dual:
                    if gdata.configSPS2.is_offline:
                        self.save_sps2_offline_data()
                    else:
                        self.save_sps2_online_data()

            except:
                logging.exception("excpetion occured at SpsOfflineTask.start")
            finally:
                await asyncio.sleep(2)

    def save_sps_online_data(self):
        DataSaver.save(
            'sps',
            gdata.configSPS.torque, gdata.configSPS.thrust, gdata.configSPS.speed
        )

    def save_sps2_online_data(self):
        DataSaver.save(
            'sps2',
            gdata.configSPS2.torque, gdata.configSPS2.thrust, gdata.configSPS2.speed
        )

    def save_sps_offline_data(self):
        DataSaver.save(
            'sps',
            gdata.configOffline.torque, gdata.configOffline.thrust, gdata.configOffline.speed
        )

    def save_sps2_offline_data(self):
        DataSaver.save(
            'sps2',
            gdata.configOffline.torque, gdata.configOffline.thrust, gdata.configOffline.speed
        )

    def stop(self):
        self.task_running = False


data_record_task: DataRecordTask = DataRecordTask()
