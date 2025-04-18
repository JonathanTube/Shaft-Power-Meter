import asyncio
import flet as ft
from db.models.data_log import DataLog
from utils.formula_cal import FormulaCalculator
from task.utc_timer_task import utc_timer
from common.global_data import gdata


class DataSaveTask:
    def __init__(self, page: ft.Page):
        self.page = page

    async def start(self):
        while True:
            await self.save_data('sps1')
            await asyncio.sleep(1)

    async def save_data(self, name: str):
        utc_date_time = utc_timer.get_utc_date_time()
        if name == 'sps1':
            speed = gdata.sps1_speed
            thrust = gdata.sps1_thrust
            torque = gdata.sps1_torque
            rounds = gdata.sps1_rounds
            power = FormulaCalculator.calculate_instant_power(torque, speed)
            gdata.sps1_power = power
        else:
            speed = gdata.sps2_speed
            thrust = gdata.sps2_thrust
            torque = gdata.sps2_torque
            rounds = gdata.sps2_rounds
            power = FormulaCalculator.calculate_instant_power(torque, speed)
            gdata.sps2_power = power



        try:
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
