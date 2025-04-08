from pymodbus.client import ModbusTcpClient


class PlcClient:
    def __init__(self, host: str, port: int):
        self.client = ModbusTcpClient(host=host, port=port)

    def read_register(self, dec_address):
        try:
            address = int(dec_address)
            resp = self.client.read_holding_registers(address)
            if resp.isError():
                print(f"Modbus Error: {resp}")
                return None
            return resp.registers
        except Exception as e:
            print(f"Runtime Error: {e}")
            return None

    def write_register(self, dec_address, value):
        try:
            address = int(dec_address)
            resp = self.client.write_register(address, value)
            return not resp.isError()
        except Exception as e:
            print(f"Runtime Error: {e}")
            return False

    def close(self):
        if self.client and self.client.is_socket_open():
            try:
                self.client.close()
            except Exception as e:
                print(f"Runtime Error: {e}")


# 调用函数读取地址 12288
result = PlcClient(host='192.168.1.100', port=502).read_register(412298)
if result is not None:
    print(f"Read value: {result}")

# PlcClient.write_register(12290, 11)
# PlcClient.write_register(12291, 12)

# PlcClient.client.close()
