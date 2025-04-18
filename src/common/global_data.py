class GlobalData:
    def __init__(self):
        self.breach_eexi_occured = False
        self.alarm_occured = False
        self.power_overload_occured = False


gdata: GlobalData = GlobalData()
