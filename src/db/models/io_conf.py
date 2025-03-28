from peewee import IntegerField, CharField, BooleanField

from ..base import BaseModel


class IOConf(BaseModel):
    plc_ip = CharField(verbose_name="PLC IP address")

    plc_port = IntegerField(verbose_name="PLC port")

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
