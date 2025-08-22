import asyncio
from common.global_data import gdata
from jm3846.JM3846_util import JM3846Util

# N秒采集


class JM3846DataHandlerForNs:
    def __init__(self) -> None:
        self._is_running = False
        self.name = None

    def is_running(self):
        return self._is_running

    async def start(self, name):
        self.name = name
        self._is_running = True
        while self._is_running:
            seconds = gdata.configPreference.data_collection_seconds_range
            if gdata.configTest.test_mode_running:
                await asyncio.sleep(seconds)
                continue

            # 清理数据
            if self.name == 'sps':
                # 处理数据
                ch0_ad, ch1_ad, rpm = JM3846Util.get_avg(self.name, gdata.configSPS.accumulated_data_ad0_ad1_speed)
                # ad值不可能为0，为0，不处理
                if ch0_ad != 0:
                    gdata.configSPS.ad0 = ch0_ad
                    gdata.configSPS.ad1 = ch1_ad
                    gdata.configSPS.speed = rpm
                    gdata.configSPS.torque = JM3846Util.cal_torque(self.name, ch0_ad)
                    gdata.configSPS.thrust = JM3846Util.cal_thrust(self.name, ch1_ad)
                    gdata.configSPS.accumulated_data_ad0_ad1_speed.clear()
            else:
                # 处理数据
                ch0_ad, ch1_ad, rpm = JM3846Util.get_avg(self.name, gdata.configSPS2.accumulated_data_ad0_ad1_speed)
                # ad值不可能为0，为0，不处理
                if ch0_ad != 0:
                    gdata.configSPS2.ad0 = ch0_ad
                    gdata.configSPS2.ad1 = ch1_ad
                    gdata.configSPS2.speed = rpm
                    gdata.configSPS2.torque = JM3846Util.cal_torque(self.name, ch0_ad)
                    gdata.configSPS2.thrust = JM3846Util.cal_thrust(self.name, ch1_ad)
                    gdata.configSPS2.accumulated_data_ad0_ad1_speed.clear()
            # 等待数据累积
            await asyncio.sleep(seconds)

    def stop(self):
        self._is_running = False


jm3846_data_handler_for_ns: JM3846DataHandlerForNs = JM3846DataHandlerForNs()
