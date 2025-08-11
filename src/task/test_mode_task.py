import asyncio
import random
import logging
from peewee import fn
from db.models.counter_log import CounterLog
from db.models.data_log import DataLog
from db.models.system_settings import SystemSettings
from common.global_data import gdata
from db.models.event_log import EventLog
from db.models.report_info import ReportInfo


class TestModeTask:
    """
    测试模式任务
    用于在没有真实SPS数据时，按设定范围生成随机数据。
    """

    def __init__(self):
        # 范围配置
        self.min_torque = 0
        self.max_torque = 0
        self.min_speed = 0
        self.max_speed = 0
        self.min_thrust = 0
        self.max_thrust = 0

        self.is_running = False

    # ===================== 配置方法 =====================
    def set_torque_range(self, min_val: float, max_val: float):
        """设置扭矩范围"""
        self.min_torque = min_val
        self.max_torque = max_val
        logging.info(f"[TestMode] 扭矩范围已设置: {min_val} ~ {max_val}")

    def set_speed_range(self, min_val: float, max_val: float):
        """设置转速范围"""
        self.min_speed = min_val
        self.max_speed = max_val
        logging.info(f"[TestMode] 转速范围已设置: {min_val} ~ {max_val}")

    def set_thrust_range(self, min_val: float, max_val: float):
        """设置推力范围"""
        self.min_thrust = min_val
        self.max_thrust = max_val
        logging.info(f"[TestMode] 推力范围已设置: {min_val} ~ {max_val}")

    # ===================== 运行控制 =====================
    async def start(self):
        """启动测试模式数据生成"""
        if self.is_running:
            logging.warning("[TestMode] 测试模式已在运行，忽略启动请求")
            return

        logging.info("[TestMode] 启动测试模式数据生成")
        gdata.configTest.start_time = gdata.configDateTime.utc
        self.is_running = True
        asyncio.create_task(self._generate_random_data())

    def stop(self):
        """停止测试模式数据生成，并清理数据"""
        logging.info("[TestMode] 停止测试模式，清理测试数据")
        self.is_running = False

        try:
            # 删除测试期间产生的数据
            DataLog.delete().where(DataLog.utc_date_time >= gdata.configTest.start_time).execute()

            event_logs = EventLog.select().where(EventLog.started_at >= gdata.configTest.start_time)
            for event in event_logs:
                EventLog.delete().where(EventLog.id == event.id).execute()
                ReportInfo.delete().where(ReportInfo.event_log == event).execute()

            # 重新统计总计数
            valid_data_log = DataLog.select(
                fn.sum(DataLog.speed).alias("speed"),
                fn.sum(DataLog.power).alias("power"),
                fn.count(DataLog.id).alias("times")
            ).dicts().get()

            CounterLog.update(
                total_speed=valid_data_log['speed'] or 0,
                total_power=valid_data_log['power'] or 0,
                times=valid_data_log['times'] or 0
            ).execute()

            # 清零实时数据
            for sps in [gdata.configSPS, gdata.configSPS2]:
                sps.speed = 0
                sps.power = 0
                sps.torque = 0
                sps.thrust = 0
                sps.power_history = []

        except Exception:
            logging.exception("[TestMode] 停止测试模式时出错")

    # ===================== 内部方法 =====================
    async def _generate_random_data(self):
        """后台任务：按范围生成随机数据"""
        try:
            system_settings: SystemSettings = SystemSettings.get()
            amount_of_propeller = system_settings.amount_of_propeller

            while self.is_running:
                self._save_generated_data('sps')
                if amount_of_propeller == 2:
                    self._save_generated_data('sps2')

                await asyncio.sleep(2)  # 与 SPS 采集周期一致

        except Exception:
            logging.exception("[TestMode] 数据生成任务异常，测试模式停止")
            self.is_running = False

    def _save_generated_data(self, name: str):
        """保存随机生成的模拟数据到全局变量"""
        try:
            instant_torque = int(random.uniform(self.min_torque, self.max_torque))
            instant_speed = int(random.uniform(self.min_speed, self.max_speed))
            instant_thrust = int(random.uniform(self.min_thrust, self.max_thrust))

            if name == 'sps':
                gdata.configSPS.torque = instant_torque
                gdata.configSPS.thrust = instant_thrust
                gdata.configSPS.speed = instant_speed
            elif name == 'sps2':
                gdata.configSPS2.torque = instant_torque
                gdata.configSPS2.thrust = instant_thrust
                gdata.configSPS2.speed = instant_speed

            logging.debug(f"[TestMode] {name} 生成数据: Torque={instant_torque}, Thrust={instant_thrust}, Speed={instant_speed}")

        except Exception:
            logging.exception(f"[TestMode] 保存{name}数据时出错")


# 单例
test_mode_task: TestModeTask = TestModeTask()
