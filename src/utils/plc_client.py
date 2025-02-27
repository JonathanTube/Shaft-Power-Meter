import snap7
from snap7.util import get_real
from snap7.exceptions import Snap7Exception


class PLCClient:
    def __init__(self, plc_ip, rack, slot):
        self.plc_ip = plc_ip
        self.rack = rack
        self.slot = slot
        self.plc = snap7.client.Client()

    def connect(self):
        try:
            self.plc.connect(self.plc_ip, self.rack, self.slot)
            if not self.plc.get_connected():
                print("Failed to connect to the PLC.")
                return False
            return True
        except Snap7Exception as e:
            print(f"Error connecting to PLC: {e}")
            return False

    def disconnect(self):
        self.plc.disconnect()

    def read_data(self, db_number, start, size):
        try:
            data = self.plc.read_area(
                snap7.types.Areas.DB, db_number, start, size)
            return data
        except Snap7Exception as e:
            print(f"Error reading data from PLC: {e}")
            return None

    def parse_data(self, data):
        # Example of parsing data
        # Assuming torque is a real number at offset 0
        torque = get_real(data, 0)
        # Assuming thrust is a real number at offset 4
        thrust = get_real(data, 4)
        return torque, thrust
