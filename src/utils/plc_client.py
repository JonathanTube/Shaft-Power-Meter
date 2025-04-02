from pymodbus.client import ModbusTcpClient
from db.models.io_conf import IOConf


class PlcClient:
    def __init__(self):
        io_conf = IOConf.get()
        host = io_conf.plc_host
        port = io_conf.plc_port

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
# result = PlcClient.read_register(12288)
# if result is not None:
#     print(f"Read value: {result}")

# PlcClient.write_register(12290, 11)
# PlcClient.write_register(12291, 12)

# PlcClient.client.close()
