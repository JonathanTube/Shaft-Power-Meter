import logging
import flet as ft
from matplotlib.dates import relativedelta

from db.models.date_time_conf import DateTimeConf
from db.models.zero_cal_info import ZeroCalInfo


class ZeroCalExecutorTips(ft.Card):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def build(self):
        try:
            date_time_conf: DateTimeConf = DateTimeConf.get()
            self.date_format = date_time_conf.date_format

            # 查询最新的一条进行中的记录
            self.latest_zero_cal: ZeroCalInfo = ZeroCalInfo.select().where(
                ZeroCalInfo.name == self.name
            ).order_by(ZeroCalInfo.id.desc()).first()

            zero_cal_last_performed, recommend_next_performing_time = self.get_next_performing_time()

            self.zero_cal_last_performed = ft.Text(zero_cal_last_performed)

            self.recommend_next_performing_time = ft.Text(
                recommend_next_performing_time)

            row = ft.Row(
                height=40,
                spacing=20,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(self.page.session.get(
                                "lang.zero_cal.last_performed")),
                            self.zero_cal_last_performed
                        ]),
                    ft.Row(
                        controls=[
                            ft.Text(self.page.session.get(
                                "lang.zero_cal.recommend_next_performing_time")),
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

    def get_next_performing_time(self):
        zero_cal_last_performed = "None"
        recommend_next_performing_time = "None"

        # 查询最近一次[接受]的调零记录
        self.latest_accepted_zero_cal: ZeroCalInfo = ZeroCalInfo.select().where(
            ZeroCalInfo.name == self.name
        ).order_by(ZeroCalInfo.id.desc()).first()

        if self.latest_accepted_zero_cal is not None:
            format_str = f'{self.date_format} %H:%M'
            zero_cal_last_performed = self.latest_accepted_zero_cal.utc_date_time.strftime(
                format_str)
            # 默认每隔6个月建议调零一次
            recommend_next_performing_time = (
                self.latest_accepted_zero_cal.utc_date_time +
                relativedelta(months=+6)
            ).strftime(format_str)

        return zero_cal_last_performed, recommend_next_performing_time
