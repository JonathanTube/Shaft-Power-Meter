import logging
import flet as ft
from matplotlib.dates import relativedelta
from common.global_data import gdata
from db.models.zero_cal_info import ZeroCalInfo


class ZeroCalExecutorTips(ft.Card):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.last_performed = "/"
        self.recommend_next_time = "/"

    def build(self):
        try:
            self.load_data()
            self.zero_cal_last_performed = ft.Text(value=self.last_performed)

            self.recommend_next_performing_time = ft.Text(value=self.recommend_next_time)

            row = ft.Row(
                height=40,
                spacing=20,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(self.page.session.get("lang.zero_cal.last_performed")),
                            self.zero_cal_last_performed
                        ]),
                    ft.Row(
                        controls=[
                            ft.Text(self.page.session.get("lang.zero_cal.recommend_next_performing_time")),
                            self.recommend_next_performing_time
                        ])
                ]
            )

            self.content = ft.Container(
                padding=ft.padding.symmetric(0, 10),
                content=row
            )

        except:
            logging.exception('exception occured at ZeroCalExecutorTips.build')

    def load_data(self):
        try:
            # 查询最新的一条进行中的记录
            self.latest_zero_cal: ZeroCalInfo = ZeroCalInfo.select().where(ZeroCalInfo.name == self.name).order_by(ZeroCalInfo.id.desc()).first()

            if self.latest_zero_cal is None:
                return

            format_str = f'{gdata.configDateTime.date_format} %H:%M'

            self.last_performed = self.latest_zero_cal.utc_date_time.strftime(format_str)
            # 默认每隔6个月建议调零一次
            self.recommend_next_time = (self.latest_zero_cal.utc_date_time + relativedelta(months=+6)).strftime(format_str)
        except:
            logging.exception('exception occured at ZeroCalExecutorTips.before_update')

    def before_update(self):
        self.load_data()
        self.zero_cal_last_performed.value = self.last_performed
        self.recommend_next_performing_time.value = self.recommend_next_time
