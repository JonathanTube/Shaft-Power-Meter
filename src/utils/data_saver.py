import asyncio
import logging
from common.const_alarm_type import AlarmType
from db.models.counter_log import CounterLog
from db.models.data_log import DataLog
from common.global_data import gdata
from task.sps_read_task import sps_read_task
from task.sps2_read_task import sps2_read_task
from task.plc_sync_task import plc
from utils.datetime_util import DateTimeUtil
from utils.formula_cal import FormulaCalculator
from utils.alarm_saver import AlarmSaver
from task.modbus_output_task import modbus_output
from websocket.websocket_master import ws_server


class DataSaver:
    overload = None

    @staticmethod
    async def save(name: str, torque: int, thrust: int, speed: float):
        try:
            utc = gdata.configDateTime.utc
            if utc is None:
                return

            power: int = FormulaCalculator.calculate_instant_power(torque, speed)
            DataSaver.is_overload(speed, power)

            data = {
                'utc_date_time': utc,
                'name': name,
                'speed': speed,
                'power': power,
                'ad_0_torque': torque,
                'ad_1_thrust': thrust,
                'is_overload': DataSaver.overload
            }

            if speed != 0 or torque != 0 or thrust != 0:
                await asyncio.to_thread(DataLog.insert(data).execute)

            # 主站且PLC连接时写入瞬时数据
            if gdata.configCommon.is_master:
                DataSaver._safe_create_task(plc.write_instant_data(power, torque, thrust, speed))

            # 更新计数器
            DataSaver.save_counter_manually(name, speed, power)
            DataSaver.save_counter_total(name, speed, power)

            # 发送数据到客户端
            if gdata.configCommon.is_master:
                # 主站且SPS在线时发送数据
                if name == 'sps' and sps_read_task.is_online is True:
                    DataSaver._safe_create_task(ws_server.send({
                        'type': name,
                        'test': gdata.configTest.test_mode_running,
                        'data': {
                            'torque': torque,
                            'thrust': thrust,
                            'speed': speed,
                            'gps': gdata.configGps.location,
                            'utc': DateTimeUtil.format_date(gdata.configDateTime.utc)
                        }
                    }))
                # 主站且SPS2在线时发送数据
                elif name == 'sps2' and sps2_read_task.is_online is True:
                    DataSaver._safe_create_task(ws_server.send({
                        'type': name,
                        'test': gdata.configTest.test_mode_running,
                        'data': {
                            'torque': torque,
                            'thrust': thrust,
                            'speed': speed,
                            'gps': gdata.configGps.location,
                            'utc': DateTimeUtil.format_date(gdata.configDateTime.utc)
                        }
                    }))

            # 更新内存缓存
            if name == 'sps':
                gdata.configSPS.torque = torque
                gdata.configSPS.thrust = thrust
                gdata.configSPS.speed = speed
                gdata.configSPS.power = power
            else:
                gdata.configSPS2.torque = torque
                gdata.configSPS2.thrust = thrust
                gdata.configSPS2.speed = speed
                gdata.configSPS2.power = power

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

        # print(f'actual_power_percentage={actual_power_percentage}')
        # print(f'overload_power_percentage={overload_power_percentage}')

        overload = actual_power_percentage > overload_power_percentage

        # 没变化
        if overload == DataSaver.overload:
            return

        DataSaver.overload = overload

        # 有变化
        if gdata.configPropperCurve.enable_power_overload_alarm:
            if DataSaver.overload:
                DataSaver._safe_create_task(AlarmSaver.create(AlarmType.POWER_OVERLOAD))
                DataSaver._safe_create_task(plc.write_power_overload(True))
            else:
                DataSaver._safe_create_task(AlarmSaver.recovery(AlarmType.POWER_OVERLOAD))
                DataSaver._safe_create_task(plc.write_power_overload(False))

    @staticmethod
    def save_counter_manually(name: str, speed: float, power: float):
        if name == 'sps':
            if gdata.configCounterSPS.Manually.status == 'running':
                gdata.configCounterSPS.Manually.sum_speed += speed
                gdata.configCounterSPS.Manually.sum_power += power
                gdata.configCounterSPS.Manually.times += 1

                time_elapsed = gdata.configCounterSPS.Manually.seconds + gdata.configPreference.data_collection_seconds_range
                gdata.configCounterSPS.Manually.seconds = time_elapsed

                avg_power, total_energy, avg_speed = DataSaver.get_data(
                    time_elapsed,
                    gdata.configCounterSPS.Manually.sum_power,
                    gdata.configCounterSPS.Manually.sum_speed,
                    gdata.configCounterSPS.Manually.times
                )

                gdata.configCounterSPS.Manually.avg_power = avg_power
                gdata.configCounterSPS.Manually.total_energy = total_energy
                gdata.configCounterSPS.Manually.avg_speed = avg_speed
            return

        if gdata.configCounterSPS2.Manually.status == 'running':
            gdata.configCounterSPS2.Manually.sum_speed += speed
            gdata.configCounterSPS2.Manually.sum_power += power
            gdata.configCounterSPS2.Manually.times += 1

            time_elapsed = gdata.configCounterSPS2.Manually.seconds + gdata.configPreference.data_collection_seconds_range
            gdata.configCounterSPS2.Manually.seconds = time_elapsed

            avg_power, total_energy, avg_speed = DataSaver.get_data(
                time_elapsed,
                gdata.configCounterSPS2.Manually.sum_power,
                gdata.configCounterSPS2.Manually.sum_speed,
                gdata.configCounterSPS2.Manually.times
            )

            gdata.configCounterSPS2.Manually.avg_power = avg_power
            gdata.configCounterSPS2.Manually.total_energy = total_energy
            gdata.configCounterSPS2.Manually.avg_speed = avg_speed

    @staticmethod
    def save_counter_total(name: str, speed: float, power: float):
        if name == 'sps':
            gdata.configCounterSPS.Total.sum_speed += speed
            gdata.configCounterSPS.Total.sum_power += power
            gdata.configCounterSPS.Total.times += 1

            avg_power, total_energy, avg_speed = DataSaver.get_data(
                gdata.configCounterSPS.Total.seconds,
                gdata.configCounterSPS.Total.sum_power,
                gdata.configCounterSPS.Total.sum_speed,
                gdata.configCounterSPS.Total.times
            )

            gdata.configCounterSPS.Total.avg_power = avg_power
            gdata.configCounterSPS.Total.total_energy = total_energy
            gdata.configCounterSPS.Total.avg_speed = avg_speed

            time_elapsed = gdata.configCounterSPS.Total.seconds + gdata.configPreference.data_collection_seconds_range
            gdata.configCounterSPS.Total.seconds = time_elapsed
            CounterLog.update(
                sum_speed=gdata.configCounterSPS.Total.sum_speed,
                sum_power=gdata.configCounterSPS.Total.sum_power,
                times=gdata.configCounterSPS.Total.times,
                seconds=time_elapsed
            ).where(CounterLog.sps_name == 'sps').execute()
        else:
            gdata.configCounterSPS2.Total.sum_speed += speed
            gdata.configCounterSPS2.Total.sum_power += power
            gdata.configCounterSPS2.Total.times += 1

            avg_power, total_energy, avg_speed = DataSaver.get_data(
                gdata.configCounterSPS2.Total.seconds,
                gdata.configCounterSPS2.Total.sum_power,
                gdata.configCounterSPS2.Total.sum_speed,
                gdata.configCounterSPS2.Total.times
            )

            gdata.configCounterSPS2.Total.avg_power = avg_power
            gdata.configCounterSPS2.Total.total_energy = total_energy
            gdata.configCounterSPS2.Total.avg_speed = avg_speed

            time_elapsed = gdata.configCounterSPS2.Total.seconds + gdata.configPreference.data_collection_seconds_range
            gdata.configCounterSPS2.Total.seconds = time_elapsed
            CounterLog.update(
                sum_speed=gdata.configCounterSPS2.Total.sum_speed,
                sum_power=gdata.configCounterSPS2.Total.sum_power,
                times=gdata.configCounterSPS2.Total.times,
                seconds=time_elapsed
            ).where(CounterLog.sps_name == 'sps2').execute()

    def get_data(time_elapsed: int, sum_power: int, sum_speed: float, times: int):
        if times == 0:
            return (0, 0, 0.0)

        avg_power = round(sum_power/times)

        hours = time_elapsed / 3600
        total_energy = round(avg_power * hours / 1000)
        avg_speed = round(sum_speed/times, 1)
        return (avg_power, total_energy, avg_speed)
