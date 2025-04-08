from pymodbus.client import ModbusTcpClient
import time


def read_modbus_tcp():
    client = ModbusTcpClient(
        host='192.168.1.100',  # 转换网关IP
        port=502,              # Modbus TCP默认端口
        retries=3
    )

    try:
        while True:
            # 读取保持寄存器 (预设起始地址0，数量2)
            result = client.read_holding_registers(
                address=0,
                count=2,
                slave=1  # 从机地址需与网关配置一致
            )

            if result.isError():
                print("读取错误:", result)
                time.sleep(2)
                continue

            thrust = result.registers[0]
            torque = result.registers[1]
            if torque > 32767:
                torque -= 65536  # 处理16位有符号数

            print(f"读取成功 | 推力: {thrust}N, 扭力: {torque}Nm")
            time.sleep(1)

    except KeyboardInterrupt:
        print("客户端终止")
    finally:
        client.close()


if __name__ == "__main__":
    read_modbus_tcp()
