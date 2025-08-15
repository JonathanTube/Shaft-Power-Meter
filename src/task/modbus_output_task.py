import asyncio
import logging
import struct
from typing import Optional, Tuple

from pymodbus.server import StartAsyncSerialServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock

from db.models.counter_log import CounterLog
from common.global_data import gdata

logger = logging.getLogger("ModbusOutputTask")


class ModbusOutputTask:
    def __init__(self, register_size: int = 200):
        """
        这里的 register_size 仍然是 16-bit 寄存器数量。
        因为 1 个 float = 2 个 16-bit。
        """
        self.register_size = register_size
        self.slave_id = 1

        self.context: Optional[ModbusServerContext] = None
        self.server_task: Optional[asyncio.Task] = None

        self.running = False
        self._is_started = False

        self._ctx_lock = asyncio.Lock()
        self._update_lock = asyncio.Lock()

    @property
    def is_started(self):
        return self._is_started

    async def start(self):
        if self._is_started:
            logger.info("ModbusOutputTask 已启动")
            return

        port = gdata.configIO.output_com_port
        if port is None:
            logger.info("ModbusOutputTask 端口未配置")
            return

        try:
            store = ModbusSlaveContext(
                hr=ModbusSequentialDataBlock(0, [0] * self.register_size)
            )
            self.context = ModbusServerContext(slaves={self.slave_id: store}, single=False)
        except Exception:
            logger.exception("创建 Modbus 数据存储失败")
            self.context = None

        async def _run_server():
            try:
                logger.info(f"启动 Modbus RTU Server")
                await StartAsyncSerialServer(
                    context=self.context,
                    port=port,
                    framer="rtu",
                    baudrate=9600,
                    bytesize=8,
                    parity="N",
                    stopbits=1
                )
            except asyncio.CancelledError:
                logger.info("Modbus RTU Server runner 被取消")
                raise
            except Exception:
                logger.exception("Modbus RTU Server runner 异常")
            finally:
                logger.info("Modbus RTU Server runner 退出")

        self.server_task = asyncio.create_task(_run_server(), name="modbus-rtu-server")
        self._is_started = True
        self.running = True
        logger.info("ModbusOutputTask 已启动")

    async def stop(self):
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

        async with self._ctx_lock:
            self.context = None

        self._is_started = False
        logger.info("ModbusOutputTask 已停止")

    # ===== 修改点1：浮点拆分函数 =====
    @staticmethod
    def _split_float_to_registers(value: float) -> Tuple[int, int]:
        """将 float 拆成两个 16-bit（高位在前），IEEE 754 单精度"""
        b = struct.pack(">f", float(value))  # 大端
        high = struct.unpack(">H", b[0:2])[0]
        low = struct.unpack(">H", b[2:4])[0]
        return high, low

    def _gather_values_sync(self) -> list:
        """采集实时数据并转换为浮点寄存器（部分字段除以 1000，全部保留 1 位小数）"""
        vals32 = []

        # ========== SPS1 ==========
        sps_torque = round(gdata.configSPS.torque/1000, 1) if gdata.configIO.output_torque else 0.0
        sps_thrust = round(gdata.configSPS.thrust/1000, 1) if gdata.configIO.output_thrust else 0.0
        sps_power = round(gdata.configSPS.power/1000, 1) if gdata.configIO.output_power else 0.0
        sps_speed = round(gdata.configSPS.speed, 1) if gdata.configIO.output_speed else 0.0
        vals32.extend([sps_torque, sps_thrust, sps_speed, sps_power])

        # ========== SPS2 ==========
        if gdata.configCommon.amount_of_propeller == 2:
            sps2_torque = round(gdata.configSPS2.torque/1000, 1) if gdata.configIO.output_torque else 0.0
            sps2_thrust = round(gdata.configSPS2.thrust/1000, 1) if gdata.configIO.output_thrust else 0.0
            sps2_power = round(gdata.configSPS2.power/1000, 1) if gdata.configIO.output_power else 0.0
            sps2_speed = round(gdata.configSPS2.speed, 1) if gdata.configIO.output_speed else 0.0
            vals32.extend([sps2_torque, sps2_thrust, sps2_speed, sps2_power])

        # 占位：合计 avg_power / total_energy（后面替换）
        vals32.extend([0.0, 0.0])

        regs = []
        for v in vals32:
            h, l = self._split_float_to_registers(v)
            regs.extend([h, l])

        return regs

    def _get_total_avg_power_and_energy_sync(self) -> Tuple[float, float]:
        """两个浆的合计平均功率 & 总能量（结果除以 1000，保留 1 位小数）"""
        try:
            total_avg = 0.0
            total_energy = 0.0

            for sps_name in ["sps", "sps2"] if gdata.configCommon.amount_of_propeller == 2 else ["sps"]:
                counter_log: CounterLog = CounterLog.get_or_none(
                    (CounterLog.sps_name == sps_name) & (CounterLog.counter_type == 2)
                )
                if not counter_log:
                    continue

                avg_power = 0.0
                if gdata.configIO.output_avg_power and counter_log.times > 0:
                    avg_power = (counter_log.total_power / counter_log.times) / 1000  # 除以 1000
                    avg_power = round(avg_power, 1)

                energy = 0.0
                if gdata.configIO.output_sum_power and avg_power > 0:
                    start_time = counter_log.start_utc_date_time
                    if start_time and gdata.configDateTime.utc:
                        hours = (gdata.configDateTime.utc - start_time).total_seconds() / 3600
                        energy = avg_power * hours
                        energy = round(energy, 1)

                total_avg += avg_power
                total_energy += energy

            return round(total_avg, 1), round(total_energy, 1)
        except Exception:
            logger.exception("计算合计平均功率与能量失败")
            return 0.0, 0.0

    async def update_registers(self) -> None:
        if not self._is_started or not self.context:
            return

        if self._update_lock.locked():
            return

        async with self._update_lock:
            try:
                base_regs = await asyncio.to_thread(self._gather_values_sync)

                total_avg, total_energy = await asyncio.to_thread(self._get_total_avg_power_and_energy_sync)

                # 替换最后两个 float
                idx = len(base_regs) - 4  # 最后两个寄存器对
                h, l = self._split_float_to_registers(total_avg)
                base_regs[idx] = h
                base_regs[idx + 1] = l
                h2, l2 = self._split_float_to_registers(total_energy)
                base_regs[idx + 2] = h2
                base_regs[idx + 3] = l2

                async with self._ctx_lock:
                    if len(base_regs) > self.register_size:
                        base_regs = base_regs[:self.register_size]
                    self.context[self.slave_id].setValues(3, 0, base_regs)

            except Exception:
                logger.exception("update_registers 错误（整体）")


modbus_output = ModbusOutputTask()
