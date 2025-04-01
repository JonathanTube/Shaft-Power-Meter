from pymodbus.client import ModbusTcpClient

# 初始化 Modbus 连接
client = ModbusTcpClient(host='192.168.1.2', port=502)  # 替换为实际 PLC IP
UNIT_ID = 1  # 根据 PLC 配置的从机地址

def read_register(dec_address, count=1):
    try:
        # 确保地址为整数
        address = int(dec_address)
        # 提交请求（适配新版本 pymodbus）
        response = client.read_holding_registers(
            address=address,
            count=count,
            slave=UNIT_ID  # 关键字参数
        )
        # 错误检查
        if response.isError():
            print(f"Modbus Error: {response}")
            return None
        return response.registers
    except Exception as e:
        print(f"Runtime Error: {e}")
        return None

def write_register(dec_address, value):
    try:
        address = int(dec_address)
        response = client.write_register(address, value, slave=UNIT_ID)
        return not response.isError()
    except Exception as e:
        print(f"Runtime Error: {e}")
        return False

# 调用函数读取地址 12288
result = read_register(12288)
if result is not None:
    print(f"Read value: {result}")

write_register(12290, 11)
write_register(12291, 12)

client.close()  # 关闭连接
