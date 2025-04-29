from common.global_data import gdata
from db.models.alarm_log import AlarmLog
from common.const_alarm_type import AlarmType
from datetime import datetime, timedelta
from db.models.data_log import DataLog
from typing import Literal
from db.models.propeller_setting import PropellerSetting
from db.models.system_settings import SystemSettings
from db.models.preference import Preference

import logging


class PowerOverload:
    @staticmethod
    def handle_power_overlaod():
        system_settings: SystemSettings = SystemSettings.get()
        is_twins: bool = system_settings.amount_of_propeller == 2
        chk_duration: int = system_settings.eexi_breach_checking_duration
        logging.info(f"eexi_breach_checking_duration: {chk_duration}s")

        preference: Preference = Preference.get()
        data_refresh_interval: int = preference.data_refresh_interval
        logging.info(f"preference.data_refresh_interval: {data_refresh_interval}s")

        propeller_settings: PropellerSetting = PropellerSetting.get()
        is_enabled: bool = propeller_settings.alarm_enabled_of_overload_curve
        # 如果功率过载曲线报警未开启，则不进行功率过载报警
        if is_enabled == False:
            return

        logging.info('==================power_overload_task: start==================')
        # 只要有一个过载就创建过载报警
        PowerOverload.__is_overload('sps1', chk_duration, data_refresh_interval)
        if is_twins:
            PowerOverload.__is_overload('sps2', chk_duration, data_refresh_interval)
        logging.info('==================power_overload_task: end==================\n')

    @staticmethod
    def __is_overload(name: Literal['sps1', 'sps2'], chk_duration: int, refresh_interval: int):
        logging.info(f"**************{name}**************")

        start_time = gdata.utc_date_time - timedelta(seconds=chk_duration)
        logging.info(f"{name} start_time = {gdata.utc_date_time} - {chk_duration}s = {start_time}")

        # 再减去数据刷新间隔，类似滑动窗口，因为数据刷新间隔是5s，所以需要减去5s
        start_time = start_time - timedelta(seconds=refresh_interval)
        logging.info(f"{name} start_time = {gdata.utc_date_time} - {chk_duration}s - {refresh_interval}s = {start_time}")

        data = DataLog.select(DataLog.utc_date_time, DataLog.is_overload).where(DataLog.utc_date_time >= start_time, DataLog.name == name)

        if len(data) == 0:
            return

        # 计算时间差，如果时间差小于60s，则不进行处理
        start_time: datetime = data[0].utc_date_time
        logging.info(f"{name} start_time of data list = {start_time}")
        end_time: datetime = data[-1].utc_date_time
        logging.info(f"{name} end_time of data list = {end_time}")
        time_diff = abs(end_time - start_time)
        logging.info(f"{name} time_diff = {time_diff.total_seconds()}")
        if time_diff.total_seconds() < chk_duration:
            return

        logging.info(f"{name} data.length = {len(data)}")

        # 计算过载次数
        overload_times = sum(1 for item in data if item.is_overload)
        logging.info(f"{name} overload_times = {overload_times}")

        # 如果过载次数等于数据长度，则认为是过载
        if overload_times == len(data):
            # 如果未确认的过载报警为0，则创建过载报警
            count = AlarmLog.select().where(AlarmLog.alarm_type == AlarmType.POWER_OVERLOAD, AlarmLog.acknowledge_time == None).count()
            if count == 0:
                AlarmLog.create(utc_date_time=gdata.utc_date_time, alarm_type=AlarmType.POWER_OVERLOAD)
