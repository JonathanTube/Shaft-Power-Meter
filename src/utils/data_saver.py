from datetime import timedelta
import logging
from db.models.data_log import DataLog
from common.global_data import gdata
from utils.formula_cal import FormulaCalculator
from common.control_manager import ControlManager


class DataSaver:
    @staticmethod
    def save(name: str, thrust: float, torque: float, speed: float, rounds: float):
        try:
            utc_date_time = gdata.utc_date_time
            power = FormulaCalculator.calculate_instant_power(torque, speed)

            # delete invalid data
            DataLog.delete().where(DataLog.utc_date_time < utc_date_time - timedelta(weeks=4 * 3))
            # insert new data
            DataLog.create(
                utc_date_time=utc_date_time,
                name=name,
                speed=speed,
                power=power,
                thrust=thrust,
                torque=torque,
                rounds=rounds
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

            ControlManager.on_instant_data_refresh()
        except Exception as e:
            logging.error(f"data saver error: {e}")
