import asyncio
import random
import logging
from common.global_data import gdata
from db.table_init import TableInit
from utils.formula_cal import FormulaCalculator
from websocket.websocket_master import ws_server


class TestModeTask:
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
        """启动测试模式数据生成（异步）"""
        if self.is_running:
            logging.warning("[TestMode] 测试模式已在运行，忽略启动请求")
            return

        logging.info("[TestMode] 启动测试模式数据生成")
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
        logging.info("[TestMode] 停止测试模式，清理测试数据")
        self.is_running = False

        # 取消后台任务（如果存在）
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await asyncio.wait_for(self._task, timeout=2)
            except asyncio.CancelledError:
                pass
            except asyncio.TimeoutError:
                logging.warning("[TestMode] 后台任务取消超时，继续进行清理")
            except Exception:
                logging.exception("[TestMode] 等待后台任务结束时出错")
            finally:
                self._task = None

        TableInit.cleanup()
        # counter是唯一需要初始化的
        gdata.configCounterSPS.set_default_value()
        gdata.configCounterSPS2.set_default_value()

    async def _generate_random_data(self):
        """后台任务：按范围生成随机数据（异步）"""
        try:
            # 在循环里尽量把阻塞操作放到线程池
            while self.is_running:
                # 生成并保存到内存（对 gdata 的赋值很快，允许在事件循环中做）
                try:
                    await self._save_generated_data('sps')
                    if gdata.configCommon.is_twins:
                        await self._save_generated_data('sps2')
                except Exception:
                    logging.exception("[TestMode] 生成或保存随机数据时出错")

                try:
                    # 测试模式，强制1s一次***
                    await asyncio.sleep(1)
                except asyncio.CancelledError:
                    # 如果任务被取消，安全退出
                    break

        except asyncio.CancelledError:
            logging.info("[TestMode] 数据生成任务被取消")
            raise
        except Exception:
            logging.exception("[TestMode] 数据生成任务异常，测试模式停止")
        finally:
            # 确保 is_running 状态被清理
            self.is_running = False

    async def _save_generated_data(self, name: str):
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
            instant_torque = round(random.uniform(min_t, max_t), 1)
            instant_speed = round(random.uniform(min_s, max_s), 1)
            instant_thrust = round(random.uniform(min_thr, max_thr), 1)

            if name == 'sps':
                gdata.configSPS.torque = instant_torque
                gdata.configSPS.thrust = instant_thrust
                gdata.configSPS.speed = instant_speed
            elif name == 'sps2':
                gdata.configSPS2.torque = instant_torque
                gdata.configSPS2.thrust = instant_thrust
                gdata.configSPS2.speed = instant_speed

            power = FormulaCalculator.calculate_instant_power(instant_torque, instant_speed)
            if gdata.configCommon.is_master:
                # 发送数据到客户端-1s
                await ws_server.send({
                    'type': f'{name}_1s',
                    'data': {
                        'power': power
                    }
                })
                # 发送数据到客户端-15s
                await ws_server.send({
                    'type': f'{name}_15s',
                    'data': {
                        'torque': instant_torque,
                        'speed': instant_speed,
                        'power': power
                    }
                })

            logging.debug(f"[TestMode] {name} 生成数据: Torque={instant_torque}, Thrust={instant_thrust}, Speed={instant_speed}")

        except Exception:
            logging.exception(f"[TestMode] 保存{name}数据时出错")


# 单例
test_mode_task: TestModeTask = TestModeTask()
