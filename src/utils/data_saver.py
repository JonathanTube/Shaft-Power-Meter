import asyncio
from datetime import timedelta
import logging
from common.const_alarm_type import AlarmType
from db.models.counter_log import CounterLog
from db.models.data_log import DataLog
from common.global_data import gdata
from utils.plc_util import plc_util
from utils.eexi_breach import EEXIBreach
from utils.formula_cal import FormulaCalculator
from utils.alarm_saver import AlarmSaver
from utils.modbus_output import modbus_output
from websocket.websocket_server import ws_server

class DataSaver:
    @staticmethod
    def save(name: str, torque: float, thrust: float, speed: float):
        try:
            utc_date_time = gdata.utc_date_time
            power = FormulaCalculator.calculate_instant_power(torque, speed)
            # delete invalid data which is over than 3 months.
            DataLog.delete().where(DataLog.utc_date_time < utc_date_time - timedelta(weeks=4 * 3)).execute()
            is_overload: bool = DataSaver.is_overload(speed, power)
            # insert new data
            DataLog.create(
                utc_date_time=utc_date_time,
                name=name,
                speed=speed,
                power=power,
                ad_0_torque=torque,
                ad_1_thrust=thrust,
                is_overload=is_overload
            )
            # 保存瞬时数据
            if gdata.plc_enabled:
                asyncio.create_task(plc_util.write_instant_data(power, torque, thrust, speed))
            # save counter log of total
            DataSaver.save_counter_total(name, speed, power)
            # save counter log of interval
            DataSaver.save_counter_interval(name, speed, power)
            # 广播给客户端数据

            asyncio.create_task(
                ws_server.broadcast({
                    'type': 'sps_data',
                    'name': name,
                    'torque': torque,
                    'thrust': thrust,
                    'rpm': speed
                })
            )

            if name == 'sps1':
                gdata.sps1_torque = torque
                gdata.sps1_thrust = thrust
                gdata.sps1_speed = speed
                gdata.sps1_power = power
                if len(gdata.sps1_power_history) > 100:
                    gdata.sps1_power_history.pop(0)
                gdata.sps1_power_history.append((power, utc_date_time))
            else:
                gdata.sps2_torque = torque
                gdata.sps2_thrust = thrust
                gdata.sps2_speed = speed
                gdata.sps2_power = power
                if len(gdata.sps2_power_history) > 100:
                    gdata.sps2_power_history.pop(0)
                gdata.sps2_power_history.append((power, utc_date_time))

            # 处理EEXI过载和恢复
            EEXIBreach.handle_breach_and_recovery()
            # 输出modbus数据
            asyncio.create_task(modbus_output.update_registers())
        except Exception:
            logging.exception("data saver error")

    @staticmethod
    def is_overload(speed, power):
        # 这里判断的是overload curve，而不是简单的判断power_of_mcr
        max_speed = gdata.speed_of_torque_load_limit
        max_power = gdata.power_of_torque_load_limit + gdata.power_of_overload
        # 相对MCR的转速百分比
        speed_percentage = speed / gdata.speed_of_mcr * 100
        # 理论的overload的功率阈值
        overload_power_percentage = round((speed_percentage / max_speed) ** 2 * max_power, 2)
        # 实际的功率百分比
        actual_power_percentage = round(power / gdata.power_of_mcr * 100, 2)
        # logging.info(f"date_saver: overload_power_percentage={overload_power_percentage}, actual_power_percentage={actual_power_percentage}")
        overload: bool = actual_power_percentage > overload_power_percentage

        if gdata.alarm_enabled_of_overload_curve:
            if overload:  # 处理功率过载
                AlarmSaver.create(AlarmType.POWER_OVERLOAD)
                # 写入plc-overload
                asyncio.create_task(plc_util.write_power_overload(True))
            else:  # 功率恢复
                # 写入plc-overload
                AlarmSaver.recovery(AlarmType.POWER_OVERLOAD)
                asyncio.create_task(plc_util.write_power_overload(False))

        return overload

    @staticmethod
    def save_counter_total(name: str, speed: float, power: float):
        cnt = CounterLog.select().where(CounterLog.sps_name == name, CounterLog.counter_type == 2).count()
        if cnt == 0:
            CounterLog.create(
                sps_name=name,
                counter_type=2,
                total_speed=speed,
                total_power=power,
                times=1,
                start_utc_date_time=gdata.utc_date_time,
                counter_status="running"
            )
        else:
            CounterLog.update(
                total_speed=CounterLog.total_speed + speed,
                total_power=CounterLog.total_power + power,
                times=CounterLog.times + 1
            ).where(
                CounterLog.sps_name == name,
                CounterLog.counter_type == 2
            ).execute()

    @staticmethod
    def save_counter_interval(name: str, speed: float, power: float):
        cnt = CounterLog.select().where(CounterLog.sps_name == name, CounterLog.counter_type == 1, CounterLog.counter_status == "running").count()
        # the intervar counter hasn't been started since the cnt is 0
        if cnt == 0:
            return

        CounterLog.update(
            total_speed=CounterLog.total_speed + speed,
            total_power=CounterLog.total_power + power,
            times=CounterLog.times + 1
        ).where(
            CounterLog.sps_name == name,
            CounterLog.counter_type == 1
        ).execute()
