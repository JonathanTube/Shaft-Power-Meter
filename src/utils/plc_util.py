import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
from common.const_alarm_type import AlarmType
from db.models.alarm_log import AlarmLog
from common.global_data import gdata
from db.models.io_conf import IOConf


class PLCUtil:
    plc_client: ModbusTcpClient = None

    @staticmethod
    def create_alarm_log():
        cnt: int = AlarmLog.select().where(AlarmLog.alarm_type == AlarmType.PLC_DISCONNECTED, AlarmLog.acknowledge_time == None).count()
        if cnt == 0:
            AlarmLog.create(utc_date_time=gdata.utc_date_time, alarm_type=AlarmType.PLC_DISCONNECTED)

    @staticmethod
    def connect():
        try:
            io_conf: IOConf = IOConf.get()
            PLCUtil.plc_client = ModbusTcpClient(host=io_conf.plc_ip, port=io_conf.plc_port, timeout=10, retries=3)
            PLCUtil.plc_client.connect()
        except Exception as e:
            logging.error(f"***plc connect error***: {e}")

    @staticmethod
    def read_4_20_ma_data():
        try:
            # 4-20MA对应-功率-下限
            power_range_min = PLCUtil.get_data(12298)
            # 4-20MA对应-功率-上限
            power_range_max = PLCUtil.get_data(12299)
            # 4-20MA对应-功率-偏移
            power_range_offset = PLCUtil.get_data(12300)

            # 4-20MA对应-扭矩-下限
            torque_range_min = PLCUtil.get_data(12308)
            # 4-20MA对应-扭矩-上限
            torque_range_max = PLCUtil.get_data(12309)
            # 4-20MA对应-扭矩-偏移
            torque_range_offset = PLCUtil.get_data(12310)

            # 4-20MA对应-推力-下限
            thrust_range_min = PLCUtil.get_data(12318)
            # 4-20MA对应-推力-上限
            thrust_range_max = PLCUtil.get_data(12319)
            # 4-20MA对应-推力-偏移
            thrust_range_offset = PLCUtil.get_data(12320)

            # 4-20MA对应-转速-下限
            speed_range_min = PLCUtil.get_data(12328)
            # 4-20MA对应-转速-上限
            speed_range_max = PLCUtil.get_data(12329)
            # 4-20MA对应-转速-偏移
            speed_range_offset = PLCUtil.get_data(12330)

            return {
                "power_range_min": power_range_min,
                "power_range_max": power_range_max,
                "power_range_offset": power_range_offset,
                "torque_range_min": torque_range_min,
                "torque_range_max": torque_range_max,
                "torque_range_offset": torque_range_offset,
                "thrust_range_min": thrust_range_min,
                "thrust_range_max": thrust_range_max,
                "thrust_range_offset": thrust_range_offset,
                "speed_range_min": speed_range_min,
                "speed_range_max": speed_range_max,
                "speed_range_offset": speed_range_offset
            }
        except ConnectionException as e:
            logging.error(f"plc connection error: {e}")
            PLCUtil.create_alarm_log()
            PLCUtil.connect()
        except Exception as e:
            logging.error(f"plc read 4-20ma data error: {e}")

        return {
            "power_range_min": None,
            "power_range_max": None,
            "power_range_offset": None,
            "torque_range_min": None,
            "torque_range_max": None,
            "torque_range_offset": None,
            "thrust_range_min": None,
            "thrust_range_max": None,
            "thrust_range_offset": None,
            "speed_range_min": None,
            "speed_range_max": None,
            "speed_range_offset": None
        }

    @staticmethod
    def read_instant_data():
        try:
            # get power
            power = PLCUtil.get_data(12301)
            # get speed
            speed = PLCUtil.get_data(12304)
            # get torque
            torque = PLCUtil.get_data(12302)
            # get thrust
            thrust = PLCUtil.get_data(12303)

            return (power, speed, torque, thrust)
        except ConnectionException as e:
            logging.error(f"plc connection error: {e}")
            PLCUtil.create_alarm_log()
            PLCUtil.connect()
        except Exception as e:
            logging.error(f"plc read data error: {e}")

    @staticmethod
    def get_data(address: int):
        result = PLCUtil.plc_client.read_holding_registers(address=address)
        if not result.isError():
            return result.registers[0]
        return None

    @staticmethod
    def write_data(power, torque, thrust):
        try:
            # 写入功率
            power = int(power/1000)
            PLCUtil.plc_client.write_register(12301, power)
            # 写入扭矩
            torque = int(torque/1000)
            PLCUtil.plc_client.write_register(12302, torque)
            # 写入推力
            thrust = int(thrust/1000)
            PLCUtil.plc_client.write_register(12303, thrust)
        except ConnectionException as e:
            logging.error(f"plc connection error: {e}")
            PLCUtil.create_alarm_log()
            PLCUtil.connect()
        except Exception as e:
            logging.error(f"plc write data error: {e}")
