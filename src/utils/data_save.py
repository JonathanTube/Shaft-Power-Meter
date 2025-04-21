from db.models.data_log import DataLog
from common.global_data import gdata


class DataSave:
    @staticmethod
    def save(name: str):
        try:
            utc_date_time = gdata.utc_date_time
            if name == 'sps1':
                speed = gdata.sps1_speed
                thrust = gdata.sps1_thrust
                torque = gdata.sps1_torque
                rounds = gdata.sps1_rounds
                power = gdata.sps1_power
            else:
                speed = gdata.sps2_speed
                thrust = gdata.sps2_thrust
                torque = gdata.sps2_torque
                rounds = gdata.sps2_rounds
                power = gdata.sps2_power

            DataLog.create(
                utc_date_time=utc_date_time,
                name=name,
                speed=speed,
                power=power,
                thrust=thrust,
                torque=torque,
                rounds=rounds
            )
        except Exception as e:
            print(f"Error generating data: {e}")
