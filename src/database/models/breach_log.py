from peewee import CharField, FloatField, IntegerField, Check
from src.database.base import BaseModel


class BreachLog(BaseModel):
    reason_for_power_reserve_breach = CharField(
        max_length=100, verbose_name="Reason for Power Reserve Breach")

    ship_name = CharField(max_length=100, verbose_name="船名", index=True)

    imo_number = IntegerField(
        unique=True,
        verbose_name="IMO编号",
        constraints=[Check('imo_number BETWEEN 1000000 AND 9999999')]
    )

    dwt = FloatField(verbose_name="船舶最大载荷能力（重量单位：吨）",
                     constraints=[Check('dwt > 0')])

    gt = FloatField(verbose_name="船舶总容积（无单位）", constraints=[Check('gt > 0')])

    max_unlimited_power = FloatField(  # Maximum unlimited shaft/engine power (kW)
        verbose_name="无限航区最大轴功率",
        constraints=[Check('max_unlimited_power > 0')]
    )

    limited_power = FloatField(  # Limited shaft/engine power (kW)
        verbose_name="限制作业轴功率",
        constraints=[Check('limited_power > 0')]
    )
