# task/modbus_output_task.py
# 说明：
# - 保持为串口 Modbus RTU server（StartAsyncSerialServer）
# - 支持 32-bit 值输出（每个 32-bit 占 2 个 16-bit 寄存器，高位在前）
# - 统一 start()/stop()/update_registers() 接口
# - 数据库访问与繁重计算使用 asyncio.to_thread，避免阻塞事件循环

import asyncio
import logging
from typing import Optional, Tuple

from pymodbus.server import StartAsyncSerialServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock

from db.models.io_conf import IOConf
from db.models.counter_log import CounterLog
from common.global_data import gdata

logger = logging.getLogger("ModbusOutputTask")


class ModbusOutputTask:
    def __init__(self, register_size: int = 200):
        # 寄存器数量（16-bit 寄存器个数），默认 200（即 100 个 32-bit 值）
        self.register_size = register_size
        self.slave_id = 1

        self.context: Optional[ModbusServerContext] = None
        self.server_task: Optional[asyncio.Task] = None
        self._server_runner_task: Optional[asyncio.Task] = None

        self.running = False
        self._is_started = False

        self.io_conf: Optional[IOConf] = None

        # 锁：防止并发 setValues 导致竞态
        self._ctx_lock = asyncio.Lock()
        # 防止 update_registers 并发执行
        self._update_lock = asyncio.Lock()

    @property
    def is_started(self):
        return self._is_started

    async def update_conf(self):
        """异步读取最新 IO 配置与系统设置"""
        try:
            self.io_conf = await asyncio.to_thread(IOConf.get)
        except Exception:
            logger.exception("读取 Modbus 输出配置失败")

    async def start(self):
        """启动 Modbus RTU server（如果配置了串口）"""
        if self._is_started:
            logger.info("ModbusOutputTask 已启动")
            return

        await self.update_conf()

        if not self.io_conf or not getattr(self.io_conf, "output_com_port", None):
            logger.info("Modbus 输出串口未配置，跳过启动")
            self._is_started = False
            return

        port = self.io_conf.output_com_port
        baudrate = getattr(self.io_conf, "output_baudrate", 9600)

        # 创建初始数据区（全部 0）
        try:
            store = ModbusSlaveContext(
                hr=ModbusSequentialDataBlock(0, [0] * self.register_size)
            )
            self.context = ModbusServerContext(slaves={self.slave_id: store}, single=False)
        except Exception:
            logger.exception("创建 Modbus 数据存储失败")
            self.context = None

        # 包装 StartAsyncSerialServer 的 runner，便于捕获取消
        async def _run_server():
            try:
                logger.info(f"启动 Modbus RTU Server on {port} @ {baudrate}")
                # StartAsyncSerialServer 会阻塞直到取消
                await StartAsyncSerialServer(
                    context=self.context,
                    port=port,
                    framer="rtu",
                    baudrate=baudrate,
                    bytesize=8,
                    parity="N",
                    stopbits=1
                )
            except asyncio.CancelledError:
                # 正常取消
                logger.info("Modbus RTU Server runner 被取消")
                raise
            except Exception:
                logger.exception("Modbus RTU Server runner 异常")
            finally:
                logger.info("Modbus RTU Server runner 退出")

        # 启动 runner
        self.server_task = asyncio.create_task(_run_server(), name="modbus-rtu-server")
        self._is_started = True
        self.running = True
        logger.info("ModbusOutputTask 已启动")

    async def stop(self):
        """安全停止 Modbus Server"""
        if not self._is_started:
            return

        logger.info("停止 ModbusOutputTask ...")
        self.running = False
        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass
            except Exception:
                logger.exception("等待 Modbus server 任务退出时异常")
            self.server_task = None

        # 清理上下文引用
        async with self._ctx_lock:
            try:
                self.context = None
            except Exception:
                pass

        self._is_started = False
        logger.info("ModbusOutputTask 已停止")

    # ---------- 工具函数 ----------
    @staticmethod
    def _split_to_registers(value: int) -> Tuple[int, int]:
        """
        将 32-bit 整数拆成两个 16-bit 寄存器（高位在前）
        使用无符号处理，保持与 PLC/其他设备的一致性。
        """
        uint32 = int(value) & 0xFFFFFFFF
        high = (uint32 >> 16) & 0xFFFF
        low = uint32 & 0xFFFF
        return high, low

    def _gather_values_sync(self) -> list:
        """
        在同步线程内执行的值收集（包含对 gdata 的读取与简单计算）。
        不执行数据库查询（DB 查询在外部线程执行）。
        """
        vals = []

        io = self.io_conf

        # 当 io_conf 丢失时，全部 0
        if not io:
            return [0] * (self.register_size)

        # 按你原来的逻辑：根据输出开关决定是否输出某些值
        sps_torque = int(getattr(gdata.configSPS, "torque", 0) / 100) if getattr(io, "output_torque", False) else 0
        sps_thrust = int(getattr(gdata.configSPS, "thrust", 0) / 100) if getattr(io, "output_thrust", False) else 0
        sps_speed = int(getattr(gdata.configSPS, "speed", 0) * 10) if getattr(io, "output_speed", False) else 0
        sps_power = int(getattr(gdata.configSPS, "power", 0) / 100) if getattr(io, "output_power", False) else 0

        # 平均功率与总能量的位值将由 _get_avg_power_and_energy_sync 返回
        # 这里先放占位 0，外部会替换
        vals32 = [sps_torque, sps_thrust, sps_speed, sps_power, 0, 0]

        if gdata.configCommon.amount_of_propeller == 2:
            sps2_torque = int(getattr(gdata.configSPS2, "torque", 0) / 100) if getattr(io, "output_torque", False) else 0
            sps2_thrust = int(getattr(gdata.configSPS2, "thrust", 0) / 100) if getattr(io, "output_thrust", False) else 0
            sps2_speed = int(getattr(gdata.configSPS2, "speed", 0) * 10) if getattr(io, "output_speed", False) else 0
            sps2_power = int(getattr(gdata.configSPS2, "power", 0) / 100) if getattr(io, "output_power", False) else 0
            vals32.extend([sps2_torque, sps2_thrust, sps2_speed, sps2_power, 0, 0])

        # 将每个 32-bit 值拆成两个寄存器
        regs = []
        for v in vals32:
            h, l = self._split_to_registers(v)
            regs.append(h)
            regs.append(l)

        return regs

    def _get_avg_power_and_energy_sync(self, sps_name: str) -> Tuple[int, int]:
        """
        在线程池中执行的 DB 查询，返回(avg_power, total_energy)
        与原逻辑一致：avg_power 单位缩放为 0.1W（整型），total_energy 单位为 0.1Wh（整型）
        """
        try:
            counter_log = CounterLog.get_or_none(
                (CounterLog.sps_name == sps_name) &
                (CounterLog.counter_type == 2)
            )
            if not counter_log:
                return 0, 0

            avg_power = 0
            if getattr(self.io_conf, "output_avg_power", False) and counter_log.times > 0:
                avg_power = int((counter_log.total_power / counter_log.times) / 100)

            total_energy = 0
            if getattr(self.io_conf, "output_sum_power", False) and avg_power:
                start_time = counter_log.start_utc_date_time
                if start_time is not None and getattr(gdata.configDateTime, "utc", None):
                    # 小时数
                    hours = (gdata.configDateTime.utc - start_time).total_seconds() / 3600
                    total_energy = int(avg_power * hours)
            return int(avg_power), int(total_energy)
        except Exception:
            logger.exception("计算平均功率与能量失败")
            return 0, 0

    # ---------- 对外更新接口 ----------
    async def update_registers(self) -> None:
        """
        将当前值写入内存寄存器（ModbusServerContext）。
        此方法可被外部频繁调用，但内部用锁序列化，且 DB 查询放在线程池中。
        """
        if not self._is_started or not self.context:
            return

        # 防止并发执行
        if self._update_lock.locked():
            # 如果已有更新在进行中，直接跳过本次调用（可改为排队，但为避免堆积直接丢弃）
            return

        async with self._update_lock:
            try:
                # 确保 io_conf 最新（不强制每次都加载，若需要可启用）
                # await self.update_conf()  # 如果你希望每次都实时加载配置，取消注释

                # 先在同步线程里收集基础寄存器（不含 avg/energy）
                base_regs = await asyncio.to_thread(self._gather_values_sync)

                # 再并行查询 avg/energy
                # sps avg & energy
                sps_avg, sps_energy = await asyncio.to_thread(self._get_avg_power_and_energy_sync, "sps")
                # 如果存在 sps2，则计算
                if gdata.configCommon.amount_of_propeller == 2:
                    sps2_avg, sps2_energy = await asyncio.to_thread(self._get_avg_power_and_energy_sync, "sps2")
                else:
                    sps2_avg, sps2_energy = 0, 0

                # 将 avg/energy 插回到寄存器列表对应位置
                # 我们在 _gather_values_sync 里是按顺序放置 [sps_torque,sps_thrust,sps_speed,sps_power,avg,energy,...]
                # 因而在 regs 列表中，第 4 个 32-bit 值后是 avg & energy，因此对应寄存器索引：
                regs = list(base_regs)  # 拷贝

                # 计算应该替换的寄存器对位置（每个32-bit占2个寄存器）
                # sps avg/energy 位于第 5 个 32-bit（索引从0起为第4个），寄存器偏移 = 4 * 2 = 8
                try:
                    # 替换 sps avg/energy
                    idx = 4 * 2
                    high, low = self._split_to_registers(sps_avg)
                    regs[idx] = high
                    regs[idx + 1] = low
                    idx2 = idx + 2
                    high_e, low_e = self._split_to_registers(sps_energy)
                    regs[idx2] = high_e
                    regs[idx2 + 1] = low_e
                except Exception:
                    # 若寄存器长度不够，忽略
                    logger.debug("替换 sps avg/energy 时超出长度，忽略")

                if gdata.configCommon.amount_of_propeller == 2:
                    # sps2 avg/energy 偏移：在 sps 部分后面，假设 sps 占 6 个 32-bit（12 个寄存器）
                    # sps 部分 6 个 32-bit => 12 寄存器，sps2 avg 偏移 = 12 + 4*2 = 20 （视实际顺序）
                    try:
                        # 具体偏移根据 _gather_values_sync 中顺序：sps (6 32-bit) 然后 sps2 (6 32-bit)
                        # sps2 avg 位于 sps 部分后面 4 个 32-bit 的位置：偏移 6*2 + 4*2 = 20
                        idx_base = 6 * 2
                        idx = idx_base + 4 * 2
                        high2, low2 = self._split_to_registers(sps2_avg)
                        regs[idx] = high2
                        regs[idx + 1] = low2
                        idx2 = idx + 2
                        high_e2, low_e2 = self._split_to_registers(sps2_energy)
                        regs[idx2] = high_e2
                        regs[idx2 + 1] = low_e2
                    except Exception:
                        logger.debug("替换 sps2 avg/energy 时超出长度，忽略")

                # 最后将寄存器写入 context（使用锁）
                async with self._ctx_lock:
                    try:
                        # 减小写入长度到 register_size
                        if len(regs) > self.register_size:
                            regs = regs[: self.register_size]
                        # setValues(func, address, values)
                        self.context[self.slave_id].setValues(3, 0, regs)
                    except Exception:
                        logger.exception("向 Modbus context 写入寄存器失败")
            except Exception:
                logger.exception("update_registers 错误（整体）")


# 单例实例，供项目其他地方直接 import 使用
modbus_output = ModbusOutputTask()
