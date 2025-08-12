import asyncio
import random
import logging
from peewee import fn
from db.models.counter_log import CounterLog
from db.models.data_log import DataLog
from common.global_data import gdata
from db.models.event_log import EventLog
from db.models.report_info import ReportInfo

_logger = logging.getLogger("TestModeTask")


class TestModeTask:
    """
    测试模式任务
    - 目的：在没有真实 SPS 数据时按设定范围生成随机数据。
    - 优化点：把阻塞的 DB 操作移到线程池；保存后台 task 引用以便优雅取消。
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

        # 背景任务引用（用于 stop 时取消）
        self._task: asyncio.Task | None = None

    # ===================== 配置方法 =====================
    def set_torque_range(self, min_val: float, max_val: float):
        """设置扭矩范围"""
        self.min_torque = min_val
        self.max_torque = max_val
        _logger.info(f"[TestMode] 扭矩范围已设置: {min_val} ~ {max_val}")

    def set_speed_range(self, min_val: float, max_val: float):
        """设置转速范围"""
        self.min_speed = min_val
        self.max_speed = max_val
        _logger.info(f"[TestMode] 转速范围已设置: {min_val} ~ {max_val}")

    def set_thrust_range(self, min_val: float, max_val: float):
        """设置推力范围"""
        self.min_thrust = min_val
        self.max_thrust = max_val
        _logger.info(f"[TestMode] 推力范围已设置: {min_val} ~ {max_val}")

    # ===================== 运行控制 =====================
    async def start(self):
        """启动测试模式数据生成（异步）"""
        if self.is_running:
            _logger.warning("[TestMode] 测试模式已在运行，忽略启动请求")
            return

        _logger.info("[TestMode] 启动测试模式数据生成")
        # 记录开始时间（同步操作很快，直接赋值）
        gdata.configTest.start_time = gdata.configDateTime.utc
        self.is_running = True

        # 如果已有任务但已结束，清理引用
        if self._task and self._task.done():
            self._task = None

        # 创建并保存后台任务引用（便于 stop 时取消）
        self._task = asyncio.create_task(self._generate_random_data(), name="testmode-generate")
        return self._task

    async def stop(self):
        """
        停止测试模式数据生成，并清理数据。
        - 将耗时的 DB 清理放到线程池里执行，避免阻塞事件循环（UI）。
        - 优雅取消后台任务并短时间等待。
        """
        _logger.info("[TestMode] 停止测试模式，清理测试数据")
        self.is_running = False

        # 取消后台任务（如果存在）
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await asyncio.wait_for(self._task, timeout=2)
            except asyncio.CancelledError:
                pass
            except asyncio.TimeoutError:
                _logger.warning("[TestMode] 后台任务取消超时，继续进行清理")
            except Exception:
                _logger.exception("[TestMode] 等待后台任务结束时出错")
            finally:
                self._task = None

        # 将所有耗时的 DB 操作放到线程池中执行（避免阻塞 UI / 事件循环）
        try:
            await asyncio.to_thread(self._cleanup_db_after_stop)
        except Exception:
            _logger.exception("[TestMode] 停止测试模式时执行 DB 清理出错")

    # ===================== 内部方法 =====================
    async def _generate_random_data(self):
        """后台任务：按范围生成随机数据（异步）"""
        try:
            # 在循环里尽量把阻塞操作放到线程池
            while self.is_running:
                # 生成并保存到内存（对 gdata 的赋值很快，允许在事件循环中做）
                try:
                    self._save_generated_data('sps')
                    if gdata.configCommon.amount_of_propeller == 2:
                        self._save_generated_data('sps2')
                except Exception:
                    _logger.exception("[TestMode] 生成或保存随机数据时出错")

                # 与 SPS 采集周期一致（非阻塞）
                try:
                    await asyncio.sleep(2)
                except asyncio.CancelledError:
                    # 如果任务被取消，安全退出
                    break

        except asyncio.CancelledError:
            _logger.info("[TestMode] 数据生成任务被取消")
            raise
        except Exception:
            _logger.exception("[TestMode] 数据生成任务异常，测试模式停止")
        finally:
            # 确保 is_running 状态被清理
            self.is_running = False

    def _save_generated_data(self, name: str):
        """保存随机生成的模拟数据到全局变量（尽量保持快速）"""
        try:
            # 保证 min/max 合理（如果用户设置错误，避免异常）
            if self.min_torque > self.max_torque:
                min_t, max_t = self.max_torque, self.min_torque
            else:
                min_t, max_t = self.min_torque, self.max_torque

            if self.min_speed > self.max_speed:
                min_s, max_s = self.max_speed, self.min_speed
            else:
                min_s, max_s = self.min_speed, self.max_speed

            if self.min_thrust > self.max_thrust:
                min_thr, max_thr = self.max_thrust, self.min_thrust
            else:
                min_thr, max_thr = self.min_thrust, self.max_thrust

            # random.uniform 在 min==max 时也会返回相同数值
            instant_torque = int(random.uniform(min_t, max_t))
            instant_speed = int(random.uniform(min_s, max_s))
            instant_thrust = int(random.uniform(min_thr, max_thr))

            if name == 'sps':
                gdata.configSPS.torque = instant_torque
                gdata.configSPS.thrust = instant_thrust
                gdata.configSPS.speed = instant_speed
            elif name == 'sps2':
                gdata.configSPS2.torque = instant_torque
                gdata.configSPS2.thrust = instant_thrust
                gdata.configSPS2.speed = instant_speed

            _logger.debug(f"[TestMode] {name} 生成数据: Torque={instant_torque}, Thrust={instant_thrust}, Speed={instant_speed}")

        except Exception:
            _logger.exception(f"[TestMode] 保存{name}数据时出错")

    def _cleanup_db_after_stop(self):
        """
        在独立线程中执行的同步 DB 清理逻辑：
        - 删除测试期间产生的数据
        - 删除事件及其报告
        - 重新统计 CounterLog
        - 清零 gdata 中实时数据（在主线程已经做过，但这里再保险处理）
        注意：这个函数将在 asyncio.to_thread 中运行（同步）。
        """
        try:
            # 删除 DataLog（测试期间）
            DataLog.delete().where(DataLog.utc_date_time >= gdata.configTest.start_time).execute()

            # 删除对应 event_log / report_info
            event_logs = list(EventLog.select().where(EventLog.started_at >= gdata.configTest.start_time))
            for event in event_logs:
                EventLog.delete().where(EventLog.id == event.id).execute()
                ReportInfo.delete().where(ReportInfo.event_log == event).execute()

            # 重新统计（防止 None 导致更新失败）
            valid_data_log = DataLog.select(
                fn.sum(DataLog.speed).alias("speed"),
                fn.sum(DataLog.power).alias("power"),
                fn.count(DataLog.id).alias("times")
            ).dicts().get()

            total_speed = valid_data_log.get('speed') or 0
            total_power = valid_data_log.get('power') or 0
            times = valid_data_log.get('times') or 0

            CounterLog.update(
                total_speed=total_speed,
                total_power=total_power,
                times=times
            ).execute()

            # 再次确保重置 gdata（虽然主线程也做过）
            try:
                for sps in [gdata.configSPS, gdata.configSPS2]:
                    sps.speed = 0
                    sps.power = 0
                    sps.torque = 0
                    sps.thrust = 0
                    sps.power_history = []
            except Exception:
                # gdata 可能在不同线程/生命周期变动，捕获异常但不阻塞
                _logger.exception("[TestMode] 清理 gdata 时出错")
        except Exception:
            _logger.exception("[TestMode] DB 清理失败（在线程池中执行）")


# 单例
test_mode_task: TestModeTask = TestModeTask()
