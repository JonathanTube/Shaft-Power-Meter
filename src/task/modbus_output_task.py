import asyncio
import logging
from pymodbus.server import StartAsyncSerialServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
from db.models.io_conf import IOConf
from db.models.system_settings import SystemSettings
from db.models.counter_log import CounterLog
from common.global_data import gdata


class ModbusOutputTask:
    def __init__(self):
        self.slave_id = 1
        self.context = None
        self.register_size: int = 200  # 调整为200个寄存器（100个32位值）
        self.server_task = None  # 存储异步任务
        self.running = False     # 服务器运行状态
        self.io_conf: IOConf | None = None
        self._is_started = False
        self.amount_of_propeller = 1  # 默认值，将在start()中更新

    @property
    def is_started(self):
        return self._is_started

    def update_conf(self):
        self.io_conf = IOConf.get()

    async def start(self):
        try:
            if self.running:
                logging.info("Modbus server is already running")
                self._is_started = True
                return

            self.io_conf: IOConf = IOConf.get()
            port = self.io_conf.output_com_port
            if not port:
                logging.info("Modbus output port is not set, skip starting Modbus server.")
                self._is_started = False
                return

            system_settings: SystemSettings = SystemSettings.get()
            self.amount_of_propeller = system_settings.amount_of_propeller
            self.running = True
            store = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [0] * self.register_size))
            self.context = ModbusServerContext(slaves={self.slave_id: store}, single=False)

            # 启动服务器（异步任务）
            self.server_task = asyncio.create_task(
                StartAsyncSerialServer(
                    context=self.context,
                    port=port,
                    framer="rtu",
                    baudrate=9600,
                    bytesize=8,
                    parity="N",
                    stopbits=1
                )
            )
            logging.info(f"Modbus server started on {port}")
            self._is_started = True
        except:
            logging.exception("exception occured at ModbusOutputTask.start")

    async def stop(self):
        if not self._is_started:
            return

        try:
            if self.server_task and not self.server_task.done():
                self.server_task.cancel()
                self.running = False
                logging.info("Modbus server stopped")
        except:
            logging.exception("exception occurred at stop_modbus_server")
        finally:
            self._is_started = False

    async def update_registers(self):
        if not self.running:
            return

        try:

            # 定义32位拆分函数（大端序）
            def split_to_registers(value):
                """将32位整数拆分为高16位和低16位"""
                # 使用无符号32位整数处理
                uint32_value = value & 0xFFFFFFFF
                high = (uint32_value >> 16) & 0xFFFF  # 高16位
                low = uint32_value & 0xFFFF           # 低16位
                return high, low

            sps1_torque = int(gdata.sps1_torque / 100) if self.io_conf.output_torque else 0
            sps1_thrust = int(gdata.sps1_thrust / 100) if self.io_conf.output_thrust else 0
            sps1_speed = int(gdata.sps1_speed * 10) if self.io_conf.output_speed else 0
            sps1_power = int(gdata.sps1_power / 100) if self.io_conf.output_power else 0
            sps1_avg_power, sps1_total_energy = self.get_avg_power_and_energy('sps1')
            # 构建寄存器值列表（每个值占2个寄存器）
            values = []
            for val in [sps1_torque, sps1_thrust, sps1_speed, sps1_power, sps1_avg_power, sps1_total_energy]:
                high, low = split_to_registers(val)
                values.append(high)
                values.append(low)

            if self.amount_of_propeller > 1:
                sps2_torque = int(gdata.sps2_torque / 100) if self.io_conf.output_torque else 0
                sps2_thrust = int(gdata.sps2_thrust / 100) if self.io_conf.output_thrust else 0
                sps2_speed = int(gdata.sps2_speed * 10) if self.io_conf.output_speed else 0
                sps2_power = int(gdata.sps2_power / 100) if self.io_conf.output_power else 0
                sps2_avg_power, sps2_total_energy = self.get_avg_power_and_energy('sps2')

                for val in [sps2_torque, sps2_thrust, sps2_speed, sps2_power, sps2_avg_power, sps2_total_energy]:
                    high, low = split_to_registers(val)
                    values.append(high)
                    values.append(low)

            # 更新寄存器（注意：寄存器数量翻倍）
            logging.info(f"32-bit registers updated: {values}")
            self.context[self.slave_id].setValues(3, 0, values)
        except Exception:
            logging.exception("32-bit register update failed")

    def get_avg_power_and_energy(self, sps_name: str):
        """获取32位整数的平均功率和总能量"""
        counter_log = CounterLog.get_or_none(
            CounterLog.sps_name == sps_name,
            CounterLog.counter_type == 2
        )
        if not counter_log:
            return 0, 0

        # 平均功率（单位：0.1W）
        avg_power = 0
        if self.io_conf.output_avg_power and counter_log.times > 0:
            avg_power = int((counter_log.total_power / counter_log.times) / 100)

        # 总能量（单位：0.1Wh）
        total_energy = 0
        if self.io_conf.output_sum_power and avg_power:
            start_time = counter_log.start_utc_date_time
            end_time = gdata.utc_date_time
            hours = (end_time - start_time).total_seconds() / 3600
            total_energy = int(avg_power * hours)  # 单位：0.1Wh

        return avg_power, total_energy


modbus_output: ModbusOutputTask = ModbusOutputTask()
