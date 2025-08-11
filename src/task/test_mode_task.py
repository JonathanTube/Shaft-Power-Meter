# task/test_mode_task.py
import asyncio
import logging
from common.global_data import gdata
from utils.data_saver import DataSaver


class TestModeTask:
    def __init__(self):
        self.task_running = False
        self._task = None

    async def start(self):
        """启动测试模式任务"""
        if self.task_running:
            return
        self.task_running = True
        self._task = asyncio.create_task(self._run_loop())

    async def _run_loop(self):
        while self.task_running:
            try:
                if gdata.configTest.test_mode_running:
                    # 模拟测试模式的随机数据或固定值
                    torque = gdata.configTest.test_torque
                    thrust = gdata.configTest.test_thrust
                    speed = gdata.configTest.test_speed

                    # 保存测试模式数据
                    DataSaver.save("sps", torque, thrust, speed)
                    if gdata.configCommon.amount_of_propeller == 2:
                        DataSaver.save("sps2", torque, thrust, speed)

            except Exception:
                logging.exception("TestModeTask 循环异常")
            finally:
                await asyncio.sleep(2)  # 避免占用过高CPU

    async def stop(self):
        """停止测试模式任务"""
        self.task_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._task = None


test_mode_task = TestModeTask()
