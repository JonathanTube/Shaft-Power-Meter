from pymodbus.client import ModbusTcpClient

# 连接配置（需替换实际参数）
PLC_IP = "192.168.1.100"      # 控制器IP
PORT = 502                    # Modbus默认端口
UNIT_ID = 1                   # 设备单元号

client = ModbusTcpClient(PLC_IP, port=PORT)


# 写入数字量输出（线圈）
def write_coil(address, value):
    response = client.write_coil(address, value, slave=UNIT_ID)
    return not response.isError()

# 读取保持寄存器（模拟量）


def read_register(address, count=1):
    response = client.read_holding_registers(address, count, slave=UNIT_ID)
    return response.registers if not response.isError() else None


# 示例：控制DO1输出
write_coil(0x0000, True)      # 地址参考设备手册[4](@ref)
# 示例：读取AI1模拟量
print(read_register(0x4000))  # 地址参考设备手册[4](@ref)
