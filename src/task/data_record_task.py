# task/data_record_task.py
import asyncio
import logging
from common.global_data import gdata
from utils.data_saver import DataSaver


class DataRecordTask:
    def __init__(self):
        self.task_running = False
        self._task = None

    async def start(self):
        """启动数据记录任务"""
        if self.task_running:
            return
        self.task_running = True
        self._task = asyncio.create_task(self._run_loop())

    async def _run_loop(self):
        while self.task_running:
            try:
                is_dual = gdata.configCommon.amount_of_propeller == 2

                # 测试模式
                if gdata.configTest.test_mode_running:
                    self.save_sps_online_data()
                    if is_dual:
                        self.save_sps2_online_data()
                    await asyncio.sleep(2)
                    continue

                # 处理SPS1
                if gdata.configSPS.is_offline:
                    self.save_sps_offline_data()
                else:
                    self.save_sps_online_data()

                # 处理SPS2（双螺旋桨）
                if is_dual:
                    if gdata.configSPS2.is_offline:
                        self.save_sps2_offline_data()
                    else:
                        self.save_sps2_online_data()

            except Exception:
                logging.exception("DataRecordTask 循环异常")
            finally:
                await asyncio.sleep(2)  # 控制循环频率

    def save_sps_online_data(self):
        DataSaver.save(
            "sps",
            gdata.configSPS.torque,
            gdata.configSPS.thrust,
            gdata.configSPS.speed
        )

    def save_sps2_online_data(self):
        DataSaver.save(
            "sps2",
            gdata.configSPS2.torque,
            gdata.configSPS2.thrust,
            gdata.configSPS2.speed
        )

    def save_sps_offline_data(self):
        DataSaver.save(
            "sps",
            gdata.configOffline.torque,
            gdata.configOffline.thrust,
            gdata.configOffline.speed
        )

    def save_sps2_offline_data(self):
        DataSaver.save(
            "sps2",
            gdata.configOffline.torque,
            gdata.configOffline.thrust,
            gdata.configOffline.speed
        )

    async def stop(self):
        """停止数据记录任务"""
        self.task_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._task = None


data_record_task = DataRecordTask()
