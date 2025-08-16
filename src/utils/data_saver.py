import asyncio
import logging
from datetime import datetime
from common.const_alarm_type import AlarmType
from db.models.data_log import DataLog
from common.global_data import gdata
from task.plc_sync_task import plc
from utils.eexi_breach import EEXIBreach
from utils.formula_cal import FormulaCalculator
from utils.alarm_saver import AlarmSaver
from task.modbus_output_task import modbus_output
from websocket.websocket_master import ws_server


class DataSaver:
    accumulated_data = []

    @staticmethod
    async def save(name: str, torque: int, thrust: int, speed: float):
        try:
            utc = gdata.configDateTime.utc
            if utc is None:
                return

            power: int = FormulaCalculator.calculate_instant_power(torque, speed)
            is_overload = DataSaver.is_overload(speed, power)

            DataSaver.accumulated_data.append({
                'utc_date_time': utc,
                'name': name,
                'speed': speed,
                'power': power,
                'ad_0_torque': torque,
                'ad_1_thrust': thrust,
                'is_overload': is_overload
            })

            # 每隔10s，保存瞬时数据
            if len(DataSaver.accumulated_data) >= 30:
                await asyncio.to_thread(DataLog.insert_many(DataSaver.accumulated_data).execute)
                DataSaver.accumulated_data.clear()

            # 主站且PLC连接时写入瞬时数据
            if gdata.configCommon.is_master:
                DataSaver._safe_create_task(plc.write_instant_data(power, torque, thrust, speed))

            # 更新计数器
            DataSaver.save_counter_manually(name, speed, power)
            DataSaver.save_counter_total(name, speed, power)
            DataSaver.save_counter_interval(name, speed, power)

            # 发送数据到客户端
            if gdata.configCommon.is_master:
                DataSaver._safe_create_task(ws_server.send({
                    'type': name,
                    'data': {
                        'torque': torque,
                        'thrust': thrust,
                        'speed': speed,
                        'gps': gdata.configGps.location
                    }
                }))

            # 更新内存缓存
            if name == 'sps':
                gdata.configSPS.torque = torque
                gdata.configSPS.thrust = thrust
                gdata.configSPS.speed = speed
                gdata.configSPS.power = power
                if len(gdata.configSPS.power_history) > 60:
                    gdata.configSPS.power_history.pop(0)
                else:
                    gdata.configSPS.power_history.append((power, utc))
            else:
                gdata.configSPS2.torque = torque
                gdata.configSPS2.thrust = thrust
                gdata.configSPS2.speed = speed
                gdata.configSPS2.power = power
                if len(gdata.configSPS2.power_history) > 60:
                    gdata.configSPS2.power_history.pop(0)
                else:
                    gdata.configSPS2.power_history.append((power, utc))

            # 处理EEXI过载
            EEXIBreach.handle()

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
    def is_overload(speed, power):
        max_speed = gdata.configPropperCurve.speed_of_torque_load_limit
        max_power = (gdata.configPropperCurve.power_of_torque_load_limit + gdata.configPropperCurve.power_of_overload)
        speed_percentage = speed / gdata.configPropperCurve.speed_of_mcr * 100
        overload_power_percentage = round((speed_percentage / max_speed) ** 2 * max_power, 2)
        actual_power_percentage = round(power / gdata.configPropperCurve.power_of_mcr * 100, 2)

        overload = actual_power_percentage > overload_power_percentage

        if gdata.configPropperCurve.enable_power_overload_alarm:
            if overload:
                AlarmSaver.create(AlarmType.POWER_OVERLOAD)
                DataSaver._safe_create_task(plc.write_power_overload(True))
            else:
                AlarmSaver.recovery(AlarmType.POWER_OVERLOAD)
                DataSaver._safe_create_task(plc.write_power_overload(False))

        return overload

    @staticmethod
    def save_counter_manually(name: str, speed: float, power: float):
        if name == 'sps':
            if gdata.configCounterSPS.Manually.status == 'running':
                gdata.configCounterSPS.Manually.total_speed += speed
                gdata.configCounterSPS.Manually.total_power += power
                gdata.configCounterSPS.Manually.times += 1

                avg_power, total_energy, avg_speed = DataSaver.get_data(
                    gdata.configCounterSPS.Manually.start_at,
                    gdata.configCounterSPS.Manually.total_power,
                    gdata.configCounterSPS.Manually.total_speed,
                    gdata.configCounterSPS.Manually.times
                )

                gdata.configCounterSPS.Manually.avg_power = avg_power
                gdata.configCounterSPS.Manually.total_energy = total_energy
                gdata.configCounterSPS.Manually.avg_speed = avg_speed
        else:
            if gdata.configCounterSPS2.Manually.status == 'running':
                gdata.configCounterSPS2.Manually.total_speed += speed
                gdata.configCounterSPS2.Manually.total_power += power
                gdata.configCounterSPS2.Manually.times += 1

                avg_power, total_energy, avg_speed = DataSaver.get_data(
                    gdata.configCounterSPS2.Manually.start_at,
                    gdata.configCounterSPS2.Manually.total_power,
                    gdata.configCounterSPS2.Manually.total_speed,
                    gdata.configCounterSPS2.Manually.times
                )

                gdata.configCounterSPS2.Manually.avg_power = avg_power
                gdata.configCounterSPS2.Manually.total_energy = total_energy
                gdata.configCounterSPS2.Manually.avg_speed = avg_speed

    @staticmethod
    def save_counter_total(name: str, speed: float, power: float):
        if name == 'sps':
            gdata.configCounterSPS.Total.total_speed += speed
            gdata.configCounterSPS.Total.total_power += power
            gdata.configCounterSPS.Total.times += 1

            avg_power, total_energy, avg_speed = DataSaver.get_data(
                gdata.configCounterSPS.Total.start_at,
                gdata.configCounterSPS.Total.total_power,
                gdata.configCounterSPS.Total.total_speed,
                gdata.configCounterSPS.Total.times
            )

            gdata.configCounterSPS.Total.avg_power = avg_power
            gdata.configCounterSPS.Total.total_energy = total_energy
            gdata.configCounterSPS.Total.avg_speed = avg_speed
        else:
            gdata.configCounterSPS2.Total.total_speed += speed
            gdata.configCounterSPS2.Total.total_power += power
            gdata.configCounterSPS2.Total.times += 1

            avg_power, total_energy, avg_speed = DataSaver.get_data(
                gdata.configCounterSPS2.Total.start_at,
                gdata.configCounterSPS2.Total.total_power,
                gdata.configCounterSPS2.Total.total_speed,
                gdata.configCounterSPS2.Total.times
            )

            gdata.configCounterSPS2.Total.avg_power = avg_power
            gdata.configCounterSPS2.Total.total_energy = total_energy
            gdata.configCounterSPS2.Total.avg_speed = avg_speed

    @staticmethod
    def save_counter_interval(name: str, speed: float, power: float):
        if name == 'sps':
            gdata.configCounterSPS.Interval.total_speed += speed
            gdata.configCounterSPS.Interval.total_power += power
            gdata.configCounterSPS.Interval.times += 1

            avg_power, total_energy, avg_speed = DataSaver.get_data(
                gdata.configCounterSPS.Interval.start_at,
                gdata.configCounterSPS.Interval.total_power,
                gdata.configCounterSPS.Interval.total_speed,
                gdata.configCounterSPS.Interval.times
            )

            gdata.configCounterSPS.Interval.avg_power = avg_power
            gdata.configCounterSPS.Interval.total_energy = total_energy
            gdata.configCounterSPS.Interval.avg_speed = avg_speed
        else:
            gdata.configCounterSPS2.Interval.total_speed += speed
            gdata.configCounterSPS2.Interval.total_power += power
            gdata.configCounterSPS2.Interval.times += 1

            avg_power, total_energy, avg_speed = DataSaver.get_data(
                gdata.configCounterSPS2.Interval.start_at,
                gdata.configCounterSPS2.Interval.total_power,
                gdata.configCounterSPS2.Interval.total_speed,
                gdata.configCounterSPS2.Interval.times
            )

            gdata.configCounterSPS2.Interval.avg_power = avg_power
            gdata.configCounterSPS2.Interval.total_energy = total_energy
            gdata.configCounterSPS2.Interval.avg_speed = avg_speed

    def get_data(start_time: datetime, total_power: int, total_speed: float, times: int):
        if start_time:
            time_elapsed = gdata.configDateTime.utc - start_time
            seconds = time_elapsed.total_seconds()
            avg_power = FormulaCalculator.calculate_average_power_kw(total_power, seconds)
            total_energy = FormulaCalculator.calculate_energy_kwh(avg_power)
            avg_speed = round(total_speed/times, 1)
            return (avg_power, total_energy, avg_speed)

        return (0, 0, 0.0)
