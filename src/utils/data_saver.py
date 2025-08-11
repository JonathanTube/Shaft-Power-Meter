import asyncio
import logging
from peewee import fn
from datetime import timedelta
from common.const_alarm_type import AlarmType
from db.models.counter_log import CounterLog
from db.models.data_log import DataLog
from common.global_data import gdata
from task.plc_sync_task import plc
from utils.eexi_breach import EEXIBreach
from utils.formula_cal import FormulaCalculator
from utils.alarm_saver import AlarmSaver
from task.modbus_output_task import modbus_output
from websocket.websocket_master import ws_server


class DataSaver:
    @staticmethod
    def save(name: str, torque: float, thrust: float, speed: float):
        try:
            utc_date_time = gdata.configDateTime.utc
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
            if gdata.configCommon.is_master and plc.is_connected:
                asyncio.create_task(plc.write_instant_data(power, torque, thrust, speed))

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

            if name == 'sps':
                gdata.configSPS.torque = torque
                gdata.configSPS.thrust = thrust
                gdata.configSPS.speed = speed
                gdata.configSPS.power = power
                if len(gdata.configSPS.power_history) > 60:
                    gdata.configSPS.power_history.pop(0)
                gdata.configSPS.power_history.append((power, utc_date_time))
            else:
                gdata.configSPS2.torque = torque
                gdata.configSPS2.thrust = thrust
                gdata.configSPS2.speed = speed
                gdata.configSPS2.power = power
                if len(gdata.configSPS2.power_history) > 60:
                    gdata.configSPS2.power_history.pop(0)
                gdata.configSPS2.power_history.append((power, utc_date_time))

            # 处理EEXI过载和恢复
            EEXIBreach.handle_breach_and_recovery()
            # 输出modbus数据
            asyncio.create_task(modbus_output.update_registers())
        except:
            logging.exception("data saver error")

    @staticmethod
    def is_overload(speed, power):
        # 这里判断的是overload curve，而不是简单的判断power_of_mcr
        max_speed = gdata.configPropperCurve.speed_of_torque_load_limit
        max_power = gdata.configPropperCurve.power_of_torque_load_limit + gdata.configPropperCurve.power_of_overload
        # 相对MCR的转速百分比
        speed_percentage = speed / gdata.configPropperCurve.speed_of_mcr * 100
        # 理论的overload的功率阈值
        overload_power_percentage = round((speed_percentage / max_speed) ** 2 * max_power, 2)
        # 实际的功率百分比
        actual_power_percentage = round(power / gdata.configPropperCurve.power_of_mcr * 100, 2)
        # logging.info(f"date_saver: overload_power_percentage={overload_power_percentage}, actual_power_percentage={actual_power_percentage}")
        overload: bool = actual_power_percentage > overload_power_percentage

        if gdata.configPropperCurve.alarm_enabled_of_overload_curve:
            if overload:  # 处理功率过载
                AlarmSaver.create(AlarmType.POWER_OVERLOAD)
                # 写入plc-overload
                asyncio.create_task(plc.write_power_overload(True))
            else:  # 功率恢复
                AlarmSaver.recovery(AlarmType.POWER_OVERLOAD)
                # 写入plc-overload
                asyncio.create_task(plc.write_power_overload(False))

        return overload

    @staticmethod
    def save_counter_total(name: str, speed: float, power: float):
        cnt = (
            CounterLog.select(fn.COUNT(CounterLog.id))
            .where(
                CounterLog.sps_name == name,
                CounterLog.counter_type == 2
            ).scalar()
        )
        if cnt == 0:
            CounterLog.create(
                sps_name=name,
                counter_type=2,
                total_speed=speed,
                total_power=power,
                times=1,
                start_utc_date_time=gdata.configDateTime.utc,
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
        cnt = (
            CounterLog.select(fn.COUNT(CounterLog.id))
            .where(
                CounterLog.sps_name == name,
                CounterLog.counter_type == 1,
                CounterLog.counter_status == "running"
            ).scalar()
        )
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
