import asyncio
from datetime import timedelta
import logging
from common.const_alarm_type import AlarmType
from db.models.data_log import DataLog
from common.global_data import gdata
from utils import plc_util
from utils.eexi_breach import EEXIBreach
from utils.formula_cal import FormulaCalculator
from common.control_manager import ControlManager
from utils.alarm_saver import AlarmSaver


class DataSaver:
    @staticmethod
    def save(name: str, thrust: float, torque: float, speed: float, rounds: float):
        try:
            utc_date_time = gdata.utc_date_time
            power = FormulaCalculator.calculate_instant_power(torque, speed)
            # delete invalid data
            DataLog.delete().where(DataLog.utc_date_time < utc_date_time - timedelta(weeks=4 * 3))
            is_overload: bool = DataSaver.is_overload(speed, power)
            # insert new data
            DataLog.create(
                utc_date_time=utc_date_time,
                name=name,
                speed=speed,
                power=power,
                thrust=thrust,
                torque=torque,
                rounds=rounds,
                is_overload=is_overload
            )
            if name == 'sps1':
                gdata.sps1_thrust = thrust
                gdata.sps1_torque = torque
                gdata.sps1_speed = speed
                gdata.sps1_rounds = rounds
                gdata.sps1_power = power
                if len(gdata.sps1_power_history) > 100:
                    gdata.sps1_power_history.pop()
                gdata.sps1_power_history.insert(0, (power, utc_date_time))

            else:
                gdata.sps2_thrust = thrust
                gdata.sps2_torque = torque
                gdata.sps2_speed = speed
                gdata.sps2_rounds = rounds
                gdata.sps2_power = power
                if len(gdata.sps2_power_history) > 100:
                    gdata.sps2_power_history.pop()
                gdata.sps2_power_history.insert(0, (power, utc_date_time))
                # print(f"sps2_power_history: {gdata.sps2_power_history}")

            ControlManager.on_instant_data_refresh()
            # 处理EEXI过载和恢复
            EEXIBreach.handle_breach_and_recovery()
        except Exception as e:
            logging.error(f"data saver error: {e}")

    @staticmethod
    def is_overload(speed, power):
        max_speed = gdata.speed_of_torque_load_limit
        max_power = gdata.power_of_torque_load_limit + gdata.power_of_overload
        # 相对MCR的转速百分比
        speed_percentage = speed / gdata.speed_of_mcr * 100
        # 理论的overload的功率阈值
        overload_power_percentage = round((speed_percentage / max_speed) ** 2 * max_power, 2)
        # 实际的功率百分比
        actual_power_percentage = round(power / gdata.power_of_mcr * 100, 2)
        logging.info(f"date_saver: overload_power_percentage={overload_power_percentage}, actual_power_percentage={actual_power_percentage}")
        overload: bool = actual_power_percentage > overload_power_percentage

        if overload:  # 处理功率过载
            AlarmSaver.create(AlarmType.POWER_OVERLOAD)
            # 写入plc-overload
            asyncio.create_task(plc_util.write_overload(False))
        else:  # 功率恢复
            # 写入plc-overload
            asyncio.create_task(plc_util.write_overload(True))

        return overload
