from peewee import CharField, DateTimeField, FloatField, BooleanField, IntegerField, Check
from datetime import datetime
from src.database.base import BaseModel


class PropellerSetting(BaseModel):
    # MCR operation point
    rpm_of_mcr_operating_point = FloatField(
        constraints=[Check('rpm_of_mcr_operating_point > 0')])

    shaft_power_of_mcr_operating_point = IntegerField(
        constraints=[Check('shaft_power_of_mcr_operating_point > 0')])

    # Normal propeller curve
    rpm_left_of_normal_propeller_curve = FloatField(
        constraints=[Check('rpm_left_of_normal_propeller_curve > 0')])

    bhp_left_of_normal_propeller_curve = FloatField(
        constraints=[Check('bhp_left_of_normal_propeller_curve > 0')])

    rpm_right_of_normal_propeller_curve = FloatField(
        constraints=[Check('rpm_right_of_normal_propeller_curve > 0')])

    bhp_right_of_normal_propeller_curve = FloatField(
        constraints=[Check('bhp_right_of_normal_propeller_curve > 0')])

    line_color_of_normal_propeller_curve = CharField(max_length=20)

    # Light propeller curve
    value_of_light_propeller_curve = FloatField(
        constraints=[Check('value_of_light_propeller_curve > 0')])

    line_color_of_light_propeller_curve = CharField(max_length=20)

    # Speed limit curve
    value_of_speed_limit_curve = FloatField(
        constraints=[Check('value_of_speed_limit_curve > 0')])

    line_color_of_speed_limit_curve = CharField(max_length=20)

    # Torque/Load limit curve
    rpm_left_of_torque_load_limit_curve = FloatField(
        constraints=[Check('rpm_left_of_torque_load_limit_curve > 0')])

    bhp_left_of_torque_load_limit_curve = FloatField(
        constraints=[Check('bhp_left_of_torque_load_limit_curve > 0')])

    rpm_right_of_torque_load_limit_curve = FloatField(
        constraints=[Check('rpm_right_of_torque_load_limit_curve > 0')])

    bhp_right_of_torque_load_limit_curve = FloatField(
        constraints=[Check('bhp_right_of_torque_load_limit_curve > 0')])

    line_color_of_torque_load_limit_curve = CharField(max_length=20)

    # Overload curve
    value_of_overload_curve = FloatField(
        constraints=[Check('value_of_overload_curve > 0')])

    line_color_of_overload_curve = CharField(max_length=20)

    alarm_enabled_of_overload_curve = BooleanField(default=False)

    created_at = DateTimeField(default=datetime.now)

    update_at = DateTimeField(default=datetime.now)
