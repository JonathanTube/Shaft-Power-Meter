from peewee import CharField, DateTimeField, IntegerField, Check
from datetime import datetime
from src.database.base import BaseModel, db


class ShipInfo(BaseModel):
    ship_type = CharField(verbose_name="类型")

    ship_name = CharField(verbose_name="船名")

    imo_number = CharField(verbose_name="IMO编号")

    ship_size = CharField(verbose_name="船舶大小")

    # dwt = FloatField(verbose_name="船舶最大载荷能力（重量单位：吨）",
    #                  constraints=[Check('dwt > 0')])
    #
    # gt = FloatField(verbose_name="船舶总容积（无单位）", constraints=[Check('gt > 0')])

    # max_unlimited_power = FloatField(  # Maximum unlimited shaft/engine power (kW)
    #     verbose_name="无限航区最大轴功率",
    #     constraints=[Check('max_unlimited_power > 0')]
    # )
    #
    # limited_power = FloatField(  # Limited shaft/engine power (kW)
    #     verbose_name="限制作业轴功率",
    #     constraints=[Check('limited_power > 0')]
    # )

    class Meta:
        table_name = 'ship_info'


with db:
    db.create_tables([ShipInfo], safe=True)
