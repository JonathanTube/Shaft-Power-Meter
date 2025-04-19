from datetime import datetime
class GlobalData:
    def __init__(self):
        self.utc_date_time: datetime = None
        self.system_date_time: datetime = None

        # 是否开启shapoli功能
        self.enable_shapoli = False
        # 是否开启功率过载告警
        self.enable_power_overload_alarm = False

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
        self.gps_location = None


gdata: GlobalData = GlobalData()
