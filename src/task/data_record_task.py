# task/data_record_task.py
import asyncio
import logging
from common.global_data import gdata
from utils.data_saver import DataSaver
from websocket.websocket_slave import ws_client
from task.sps_read_task import sps_read_task
from task.sps2_read_task import sps2_read_task


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

                if gdata.configTest.test_mode_running:  # 测试模式
                    await self.handle_test_mode()
                elif gdata.configCommon.is_master:     # 主机
                    await self.handle_master()
                else:                                 # 从机
                    await self.handle_slave()
            except Exception:
                logging.exception("DataRecordTask 循环异常")
            finally:
                await asyncio.sleep(2)  # 控制循环频率

    async def handle_test_mode(self):
        await self.save_sps_online_data()
        if gdata.configCommon.is_twins:
            await self.save_sps2_online_data()

    async def handle_master(self):
        # 处理SPS1
        if sps_read_task.is_online:
            await self.save_sps_online_data()
        else:
            await self.save_sps_offline_data()

        # 处理SPS2（双螺旋桨）
        if gdata.configCommon.is_twins:
            if sps2_read_task.is_online:
                await self.save_sps2_online_data()
            else:
                await self.save_sps2_offline_data()
        # await asyncio.sleep(2)
        # continue

    async def handle_slave(self):
        if ws_client.is_online:
            await self.save_sps_online_data()
            if gdata.configCommon.is_twins:
                await self.save_sps2_online_data()
        else:
            await self.save_sps_offline_data()
            if gdata.configCommon.is_twins:
                await self.save_sps2_offline_data()

    async def save_sps_online_data(self):
        await DataSaver.save("sps",
                             gdata.configSPS.torque,
                             gdata.configSPS.thrust,
                             gdata.configSPS.speed)

    async def save_sps2_online_data(self):
        await DataSaver.save("sps2",
                             gdata.configSPS2.torque,
                             gdata.configSPS2.thrust,
                             gdata.configSPS2.speed)

    async def save_sps_offline_data(self):
        await DataSaver.save("sps",
                             gdata.configOffline.torque,
                             gdata.configOffline.thrust,
                             gdata.configOffline.speed)

    async def save_sps2_offline_data(self):
        await DataSaver.save("sps2",
                             gdata.configOffline.torque,
                             gdata.configOffline.thrust,
                             gdata.configOffline.speed)

    async def stop(self):
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await asyncio.sleep(0)  # 给任务调度机会
            except asyncio.CancelledError:
                pass
        self._task = None


data_record_task = DataRecordTask()
