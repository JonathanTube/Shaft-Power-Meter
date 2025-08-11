# utils/data_saver.py
import asyncio
import logging
from peewee import fn
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
            if utc_date_time is None:
                return

            power = FormulaCalculator.calculate_instant_power(torque, speed)
            is_overload = DataSaver.is_overload(speed, power)

            # 保存瞬时数据
            DataLog.create(
                utc_date_time=utc_date_time,
                name=name,
                speed=speed,
                power=power,
                ad_0_torque=torque,
                ad_1_thrust=thrust,
                is_overload=is_overload
            )

            # 主站且PLC连接时写入瞬时数据
            if gdata.configCommon.is_master:
                DataSaver._safe_create_task(plc.write_instant_data(power, torque, thrust, speed))

            # 更新计数器
            DataSaver.save_counter_total(name, speed, power)
            DataSaver.save_counter_interval(name, speed, power)

            # 广播给客户端数据
            DataSaver._safe_create_task(ws_server.broadcast({
                'type': 'sps_data',
                'name': name,
                'torque': torque,
                'thrust': thrust,
                'rpm': speed
            }))

            # 更新内存缓存
            if name == 'sps':
                DataSaver._update_sps_data(gdata.configSPS, power, torque, thrust, speed, utc_date_time)
            else:
                DataSaver._update_sps_data(gdata.configSPS2, power, torque, thrust, speed, utc_date_time)

            # 处理EEXI过载
            EEXIBreach.handle_breach_and_recovery()

            # 更新 Modbus 输出
            DataSaver._safe_create_task(modbus_output.update_registers())

        except Exception:
            logging.exception("data saver error")

    @staticmethod
    def _safe_create_task(coro):
        """只有在事件循环运行中才创建异步任务"""
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(coro)
        except RuntimeError:
            # 没有事件循环则直接跳过或记录日志
            logging.warning("No running event loop, skipping async task creation")

    @staticmethod
    def _update_sps_data(cfg, power, torque, thrust, speed, utc_time):
        cfg.torque = torque
        cfg.thrust = thrust
        cfg.speed = speed
        cfg.power = power
        if len(cfg.power_history) > 60:
            cfg.power_history.pop(0)
        cfg.power_history.append((power, utc_time))

    @staticmethod
    def is_overload(speed, power):
        max_speed = gdata.configPropperCurve.speed_of_torque_load_limit
        max_power = (gdata.configPropperCurve.power_of_torque_load_limit + gdata.configPropperCurve.power_of_overload)
        speed_percentage = speed / gdata.configPropperCurve.speed_of_mcr * 100
        overload_power_percentage = round((speed_percentage / max_speed) ** 2 * max_power, 2)
        actual_power_percentage = round(power / gdata.configPropperCurve.power_of_mcr * 100, 2)

        overload = actual_power_percentage > overload_power_percentage

        if gdata.configPropperCurve.alarm_enabled_of_overload_curve:
            if overload:
                AlarmSaver.create(AlarmType.POWER_OVERLOAD)
                DataSaver._safe_create_task(plc.write_power_overload(True))
            else:
                AlarmSaver.recovery(AlarmType.POWER_OVERLOAD)
                DataSaver._safe_create_task(plc.write_power_overload(False))

        return overload

    @staticmethod
    def save_counter_total(name: str, speed: float, power: float):
        cnt = (
            CounterLog.select(fn.COUNT(CounterLog.id))
            .where(CounterLog.sps_name == name, CounterLog.counter_type == 2)
            .scalar()
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
