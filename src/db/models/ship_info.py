from peewee import CharField
from ..base import BaseModel


class ShipInfo(BaseModel):
    ship_type = CharField(verbose_name="类型")

    ship_name = CharField(verbose_name="船名")

    imo_number = CharField(verbose_name="IMO编号")

    ship_size = CharField(verbose_name="船舶大小")

    class Meta:
        table_name = 'ship_info'
