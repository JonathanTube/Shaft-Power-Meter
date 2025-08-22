import asyncio
from common.global_data import gdata
from jm3846.JM3846_util import JM3846Util
from utils.formula_cal import FormulaCalculator
from websocket.websocket_master import ws_server


class JM3846DataHandlerFor1s:
    def __init__(self) -> None:
        self._is_running = False
        self.name = None

    def is_running(self):
        return self._is_running

    async def start(self, name):
        self.name = name
        self._is_running = True
        while self._is_running:
            if gdata.configTest.test_mode_running:
                await asyncio.sleep(1)
                continue

            # 清理数据
            if self.name == 'sps':
                # 处理数据
                ch0_ad, _, rpm = JM3846Util.get_avg(self.name, gdata.configSPS.accumulated_data_ad0_ad1_speed_for_1s)
                # ad值不可能为0，为0，不处理
                if ch0_ad != 0:
                    torque = JM3846Util.cal_torque(self.name, ch0_ad)
                    # 直接计算power
                    power_for_1s = FormulaCalculator.calculate_instant_power(torque, rpm)

                    gdata.configSPS.power_for_1s = power_for_1s

                    if len(gdata.configSPS.power_history) > 300:
                        gdata.configSPS.power_history.pop(0)
                    else:
                        gdata.configSPS.power_history.append((power_for_1s, gdata.configDateTime.utc))

                    # 发送数据到客户端
                    if gdata.configCommon.is_master:
                        await ws_server.send({
                            'type': f'{name}_1s',
                            'data': {
                                'power': power_for_1s
                            }
                        })
                    gdata.configSPS.accumulated_data_ad0_ad1_speed_for_1s.clear()
            else:
                # 处理数据
                ch0_ad, _, rpm = JM3846Util.get_avg(self.name, gdata.configSPS2.accumulated_data_ad0_ad1_speed_for_1s)
                # ad值不可能为0，为0，不处理
                if ch0_ad != 0:
                    torque = JM3846Util.cal_torque(self.name, ch0_ad)
                    # 直接计算power
                    power_for_1s = FormulaCalculator.calculate_instant_power(torque, rpm)

                    gdata.configSPS2.power_for_1s = power_for_1s

                    if len(gdata.configSPS2.power_history) > 300:
                        gdata.configSPS2.power_history.pop(0)
                    else:
                        gdata.configSPS2.power_history.append((power_for_1s, utc))
                    # 发送数据到客户端
                    if gdata.configCommon.is_master:
                        await ws_server.send({
                            'type': f'{name}_1s',
                            'data': {
                                'power': power_for_1s
                            }
                        })
                    gdata.configSPS2.accumulated_data_ad0_ad1_speed_for_1s.clear()
            # 等待数据累积
            await asyncio.sleep(1)

    def stop(self):
        self._is_running = False


jm3846_data_handler_for_1s: JM3846DataHandlerFor1s = JM3846DataHandlerFor1s()
