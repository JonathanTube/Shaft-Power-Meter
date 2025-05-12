import asyncio
from asyncio.log import logger
from pymodbus.server import StartAsyncSerialServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
from db.models.io_conf import IOConf
from db.models.system_settings import SystemSettings
from common.global_data import gdata


class ModbusOutput:
    def __init__(self):
        self.slave_id = 1
        self.context = None
        self.register_size: int = 6
        self.amount_of_propeller: int = 1
        self.server_task = None  # 存储异步任务
        self.running = False     # 服务器运行状态

    async def start_modbus_server(self):
        if self.running:
            logger.warning("Modbus server is already running")
            return

        io_conf: IOConf = IOConf().get()
        port = io_conf.output_com_port
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
            sps1_torque = int(gdata.sps1_torque / 100)
            sps1_thrust = int(gdata.sps1_thrust / 100)
            sps1_speed = int(gdata.sps1_speed)
            sps1_power = int(gdata.sps1_power / 100)
            values = [sps1_torque, sps1_thrust, sps1_speed, sps1_power, 0, 0]

            if self.amount_of_propeller > 1:
                sps2_torque = int(gdata.sps2_torque / 100)
                sps2_thrust = int(gdata.sps2_thrust / 100)
                sps2_speed = int(gdata.sps2_speed)
                sps2_power = int(gdata.sps2_power / 100)
                values.extend([sps2_torque, sps2_thrust, sps2_speed, sps2_power, 0, 0])

            self.context[self.slave_id].setValues(3, 0, values)
            logger.info(f"Registers updated: {values}")
            return True
        except Exception as e:
            logger.error(f"更新寄存器失败: {str(e)}")
            return False


modbus_output: ModbusOutput = ModbusOutput()
