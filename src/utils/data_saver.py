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


class DataSaver:
    @staticmethod
    def save(name: str,
            ad_0, ad_0_mv_per_v: float, ad_0_microstrain, ad_0_torque: float,
            ad_1, ad_1_mv_per_v: float, ad_1_thrust: float, 
            speed: float
    ):
        try:
            utc_date_time = gdata.utc_date_time
            power = FormulaCalculator.calculate_instant_power(ad_0_torque, speed)
            # delete invalid data which is over than 3 months.
            DataLog.delete().where(DataLog.utc_date_time < utc_date_time - timedelta(weeks=4 * 3))
            is_overload: bool = DataSaver.is_overload(speed, power)
            # insert new data
            DataLog.create(
                utc_date_time=utc_date_time,
                name=name,
                speed=speed,
                power=power,

                ad_0=ad_0,
                ad_0_mv_per_v=ad_0_mv_per_v,
                ad_0_microstrain=ad_0_microstrain,
                ad_0_torque=ad_0_torque,

                ad_1=ad_1,
                ad_1_mv_per_v=ad_1_mv_per_v,
                ad_1_thrust=ad_1_thrust,
                is_overload=is_overload
            )
            # 保存瞬时数据
            if gdata.plc_enabled:
                logging.info(f"write real time data to plc: {power}, {ad_0_torque}, {ad_1_thrust}, {speed}")
                asyncio.create_task(plc_util.write_instant_data(power, ad_0_torque, ad_1_thrust, speed))
            # save counter log of total
            DataSaver.save_counter_total(name, speed, power)
            # save counter log of interval
            DataSaver.save_counter_interval(name, speed, power)
            if name == 'sps1':
                gdata.sps1_thrust = ad_1_thrust
                gdata.sps1_torque = ad_0_torque
                gdata.sps1_speed = speed
                gdata.sps1_power = power
                # 毫伏/伏 调零用
                gdata.sps1_thrust_mv_per_v = ad_1_mv_per_v
                gdata.sps1_torque_mv_per_v = ad_0_mv_per_v
                if len(gdata.sps1_power_history) > 100:
                    gdata.sps1_power_history.pop()
                gdata.sps1_power_history.insert(0, (power, utc_date_time))
            else:
                gdata.sps2_thrust = ad_1_thrust
                gdata.sps2_torque = ad_0_torque
                gdata.sps2_speed = speed
                gdata.sps2_power = power
                # 毫伏/伏 调零用
                gdata.sps2_thrust_mv_per_v = ad_1_mv_per_v
                gdata.sps2_torque_mv_per_v = ad_0_mv_per_v
                if len(gdata.sps2_power_history) > 100:
                    gdata.sps2_power_history.pop()
                gdata.sps2_power_history.insert(0, (power, utc_date_time))

            # 处理EEXI过载和恢复
            EEXIBreach.handle_breach_and_recovery()
            # 输出modbus数据
            asyncio.create_task(modbus_output.update_registers())
        except Exception as e:
            logging.error(f"data saver error: {e}")

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

        if overload:  # 处理功率过载
            AlarmSaver.create(AlarmType.POWER_OVERLOAD)
            # 写入plc-overload
            asyncio.create_task(plc_util.write_power_overload(True))
        else:  # 功率恢复
            # 写入plc-overload
            asyncio.create_task(plc_util.write_power_overload(False))

        return overload

    @staticmethod
    def save_counter_total(name: str, speed: float, power: float):
        # if speed is less than 10, it is not valid data, don't record total energy
        if speed <= 10:
            return
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
        # if speed is less than 10, it is not valid data, don't record total energy
        if speed <= 10:
            return

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
