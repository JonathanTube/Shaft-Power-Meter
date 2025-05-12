import asyncio
from asyncio.log import logger
from pymodbus.server import StartAsyncSerialServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
from db.models.io_conf import IOConf
from db.models.system_settings import SystemSettings
from db.models.counter_log import CounterLog
from common.global_data import gdata


class ModbusOutput:
    def __init__(self):
        self.slave_id = 1
        self.context = None
        self.register_size: int = 6
        self.amount_of_propeller: int = 1
        self.server_task = None  # 存储异步任务
        self.running = False     # 服务器运行状态
        self.io_conf: IOConf | None = None

    async def start_modbus_server(self):
        if self.running:
            logger.warning("Modbus server is already running")
            return

        self.io_conf: IOConf = IOConf().get()
        port = self.io_conf.output_com_port
        if not port:
            logger.warning("Modbus output port is not set")
            return

        system_settings: SystemSettings = SystemSettings().get()
        self.amount_of_propeller = system_settings.amount_of_propeller

        register_size = 6 * self.amount_of_propeller

        self.running = True
        store = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, [0] * register_size))
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
        logger.info(f"Modbus server started on {port}")

    async def stop_modbus_server(self):
        if self.server_task and not self.server_task.done():
            self.server_task.cancel()
            self.running = False
            logger.info("Modbus server stopped")

    async def update_registers(self):
        try:
            sps1_torque = int(gdata.sps1_torque / 100) if self.io_conf.output_torque else 0
            sps1_thrust = int(gdata.sps1_thrust / 100) if self.io_conf.output_thrust else 0
            sps1_speed = int(gdata.sps1_speed) if self.io_conf.output_speed else 0
            sps1_power = int(gdata.sps1_power / 100) if self.io_conf.output_power else 0
            sps1_average_power, sps1_total_energy = self.get_average_power_and_total_energy('sps1')
            values = [sps1_torque, sps1_thrust, sps1_speed, sps1_power, sps1_average_power, sps1_total_energy]

            if self.amount_of_propeller > 1:
                sps2_torque = int(gdata.sps2_torque / 100) if self.io_conf.output_torque else 0
                sps2_thrust = int(gdata.sps2_thrust / 100) if self.io_conf.output_thrust else 0
                sps2_speed = int(gdata.sps2_speed) if self.io_conf.output_speed else 0
                sps2_power = int(gdata.sps2_power / 100) if self.io_conf.output_power else 0
                sps2_average_power, sps2_total_energy = self.get_average_power_and_total_energy('sps2')
                values.extend([sps2_torque, sps2_thrust, sps2_speed, sps2_power, sps2_average_power, sps2_total_energy])

            self.context[self.slave_id].setValues(3, 0, values)
            logger.info(f"Registers updated: {values}")
            return True
        except Exception as e:
            logger.error(f"更新寄存器失败: {str(e)}")
            return False

    def get_average_power_and_total_energy(self, sps_name: str):
        counter_log: CounterLog = CounterLog.get_or_none(CounterLog.sps_name == sps_name, CounterLog.counter_type == 2)
        if counter_log is None:
            return 0, 0

        if self.io_conf.output_avg_power:
            average_power = counter_log.total_power / counter_log.times
            # 转换的到kw，保留1位小数，最小0.1kw，所以乘以10，即除以100
            average_power = int(average_power / 100)
        else:
            average_power = 0

        if self.io_conf.output_sum_power:
            start_time = counter_log.start_utc_date_time
            end_time = gdata.utc_date_time
            hours = (end_time - start_time).total_seconds() / 3600
            total_energy = int(average_power * hours)  # kWh，保留1位小数，最小0.1kwh，所以乘以10，power已经是/100了，所以这里不用处理
        else:
            total_energy = 0

        return average_power, total_energy


modbus_output: ModbusOutput = ModbusOutput()
