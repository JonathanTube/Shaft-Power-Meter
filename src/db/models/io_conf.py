from peewee import IntegerField, CharField, BooleanField, FloatField

from ..base import BaseModel


class IOConf(BaseModel):
    plc_ip = CharField(verbose_name="PLC IP address")

    plc_port = IntegerField(verbose_name="PLC port")

    power_range_min = FloatField(verbose_name="4-20Ma,功率最小值", default=0)
    power_range_max = FloatField(verbose_name="4-20Ma,功率最大值", default=0)
    power_range_offset = FloatField(verbose_name="4-20Ma,功率偏移量", default=0)

    speed_range_min = FloatField(verbose_name="4-20Ma,转速最小值", default=0)
    speed_range_max = FloatField(verbose_name="4-20Ma,转速最大值", default=0)
    speed_range_offset = FloatField(verbose_name="4-20Ma,转速偏移量", default=0)

    torque_range_min = FloatField(verbose_name="4-20Ma,扭力最小值", default=0)
    torque_range_max = FloatField(verbose_name="4-20Ma,扭力最大值", default=0)
    torque_range_offset = FloatField(verbose_name="4-20Ma,扭力偏移量", default=0)

    thrust_range_min = FloatField(verbose_name="4-20Ma,推力最小值", default=0)
    thrust_range_max = FloatField(verbose_name="4-20Ma,推力最大值", default=0)
    thrust_range_offset = FloatField(verbose_name="4-20Ma,推力偏移量", default=0)

    gps_ip = CharField(verbose_name="GPS IP address", default="")
    gps_port = IntegerField(verbose_name="GPS port", default=0)

    modbus_ip = CharField(verbose_name="Modbus IP address", default="")
    modbus_port = IntegerField(verbose_name="Modbus port", default=0)

    output_torque = BooleanField(verbose_name="Torque(kN)", default=False)

    output_thrust = BooleanField(verbose_name="Thrust(kN)", default=False)

    output_power = BooleanField(verbose_name="Power(kw)", default=False)

    output_speed = BooleanField(verbose_name="Speed(kN)", default=False)

    output_avg_power = BooleanField(
        verbose_name="Average Power(kw)", default=False)

    output_sum_power = BooleanField(
        verbose_name="Sum of Power(kw)", default=False)

    class Meta:
        table_name = 'io_conf'
