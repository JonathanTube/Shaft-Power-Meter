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
                is_dual = gdata.amount_of_propeller == 2
                # 测试模式打开
                if gdata.test_mode_running:
                    self.save_sps_online_data()
                    if is_dual:
                        self.save_sps2_online_data()
                    continue



                # 测试模式关闭
                if gdata.sps_offline:
                    self.save_sps_offline_data()
                else:
                    self.save_sps_online_data()

                if is_dual:
                    if gdata.sps2_offline:
                        self.save_sps2_offline_data()
                    else:
                        self.save_sps2_online_data()
                        
            except:
                logging.exception("excpetion occured at SpsOfflineTask.start")
            finally:
                await asyncio.sleep(2)

    def save_sps_online_data(self):
        DataSaver.save('sps', gdata.sps_torque, gdata.sps_thrust, gdata.sps_speed)

    def save_sps2_online_data(self):
        DataSaver.save('sps2', gdata.sps2_torque, gdata.sps2_thrust, gdata.sps2_speed)
    
    def save_sps_offline_data(self):
        DataSaver.save('sps', gdata.sps_offline_torque, gdata.sps_offline_thrust, gdata.sps_offline_speed)

    def save_sps2_offline_data(self):
        DataSaver.save('sps2', gdata.sps_offline_torque, gdata.sps_offline_thrust, gdata.sps_offline_speed)

    def stop(self):
        self.task_running = False

data_record_task:DataRecordTask = DataRecordTask()
