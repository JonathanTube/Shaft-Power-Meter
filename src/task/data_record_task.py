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
                if gdata.configSPS.sps_offline:
                    self.save_sps_offline_data()
                else:
                    self.save_sps_online_data()

                if is_dual:
                    if gdata.configSPS2.sps2_offline:
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
            gdata.configSPS.sps_torque, gdata.configSPS.sps_thrust, gdata.configSPS.sps_speed
        )

    def save_sps2_online_data(self):
        DataSaver.save(
            'sps2',
            gdata.configSPS2.sps_torque, gdata.configSPS2.sps_thrust, gdata.configSPS2.sps_speed
        )

    def save_sps_offline_data(self):
        DataSaver.save(
            'sps',
            gdata.configOffline.sps_offline_torque, gdata.configOffline.sps_offline_thrust, gdata.configOffline.sps_offline_speed
        )

    def save_sps2_offline_data(self):
        DataSaver.save(
            'sps2',
            gdata.configOffline.sps_offline_torque, gdata.configOffline.sps_offline_thrust, gdata.configOffline.sps_offline_speed
        )

    def stop(self):
        self.task_running = False


data_record_task: DataRecordTask = DataRecordTask()
