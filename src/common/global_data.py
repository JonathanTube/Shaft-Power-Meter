class GlobalData:
    def __init__(self):
        self.breach_eexi_occured = False
        self.alarm_occured = False
        self.power_overload_occured = False

        self.sps1_speed = 0
        self.sps1_power = 0
        self.sps1_torque = 0
        self.sps1_thrust = 0
        self.sps1_rounds = 0

        self.sps2_speed = 0
        self.sps2_power = 0
        self.sps2_torque = 0
        self.sps2_thrust = 0
        self.sps2_rounds = 0


gdata: GlobalData = GlobalData()
