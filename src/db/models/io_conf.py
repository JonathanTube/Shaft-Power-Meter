from peewee import IntegerField, CharField, BooleanField, FloatField

from ..base import BaseModel


class IOConf(BaseModel):
    plc_enabled = BooleanField(verbose_name="PLC enabled", default=False)

    plc_ip = CharField(verbose_name="PLC IP address")

    plc_port = IntegerField(verbose_name="PLC port")

    gps_ip = CharField(verbose_name="GPS IP address", default="")
    gps_port = IntegerField(verbose_name="GPS port", default=0)

    hmi_server_ip = CharField(verbose_name="HMI server IP address", default="127.0.0.1")
    hmi_server_port = IntegerField(verbose_name="HMI server port", default=8001)

    sps1_ip = CharField(verbose_name="SPS1 IP address", default="")
    sps1_port = IntegerField(verbose_name="SPS1 port", default=502)

    sps2_ip = CharField(verbose_name="SPS2 IP address", default="")
    sps2_port = IntegerField(verbose_name="SPS2 port", default=502)

    output_torque = BooleanField(verbose_name="Torque(kN)", default=False)

    output_thrust = BooleanField(verbose_name="Thrust(kN)", default=False)

    output_power = BooleanField(verbose_name="Power(kw)", default=False)

    output_speed = BooleanField(verbose_name="Speed(kN)", default=False)

    output_avg_power = BooleanField(verbose_name="Average Power(kw)", default=False)

    output_sum_power = BooleanField(verbose_name="Sum of Power(kw)", default=False)

    output_com_port = CharField(verbose_name="COM port", null=True)

    class Meta:
        table_name = 'io_conf'
