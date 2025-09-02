import threading
import flet as ft
import logging
from datetime import timedelta
from db.models.data_log import DataLog
from ui.home.trendview.diagram import TrendViewDiagram
from typing import Literal
from peewee import fn
from common.global_data import gdata
from utils.datetime_util import DateTimeUtil
import asyncio


class TrendView(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = 10
        self.start_date = gdata.configDateTime.utc
        self.end_date = gdata.configDateTime.utc

    def build(self):
        try:

            # 当前时间
            now = gdata.configDateTime.utc
            # 24 小时前
            self.start_date = now - timedelta(hours=24)
            self.end_date = now

            self.sps_chart = TrendViewDiagram()

            top_block = ft.Row(
                height=50,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Text(DateTimeUtil.format_date(self.start_date, f'    {gdata.configDateTime.date_format} %H:%M:%S')),
                    ft.Text(" - "),
                    ft.Text(DateTimeUtil.format_date(self.end_date, f'{gdata.configDateTime.date_format} %H:%M:%S')),
                    ft.Button(text=self.page.session.get('lang.button.refresh'), on_click=lambda e: self._on_click())
                ])

            if gdata.configCommon.is_twins:
                self.sps2_chart = TrendViewDiagram()
                # Tabs must contain only Tab items; place header row above Tabs
                self.content = ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        top_block,
                        ft.Tabs(
                            expand=True,
                            tabs=[
                                ft.Tab(text='SPS', content=self.sps_chart),
                                ft.Tab(text='SPS2', content=self.sps2_chart)
                            ]
                        )
                    ]
                )
            else:
                self.content = ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        top_block,
                        self.sps_chart
                    ]
                )
        except:
            logging.exception('exception occured at TrendView.build')

    def did_mount(self):
        # use page.run_task to run async loading on UI event loop
        if self.page:
            self.page.run_task(self.load_data_async)

    def before_update(self):
        self.end_date = gdata.configDateTime.utc

    def _on_click(self):
        if self.page:
            self.end_date = gdata.configDateTime.utc
            self.page.run_task(self.load_data_async)

    async def load_data_async(self):
        await self.fetch_and_update_async("sps")
        if gdata.configCommon.is_twins:
            await self.fetch_and_update_async("sps2")

    def _apply_chart_update(self, chart: TrendViewDiagram, data_logs):
        if chart and chart.page:
            chart.update_chart(data_logs)
            chart.update()

    async def fetch_and_update_async(self, name):
        data_logs = await asyncio.to_thread(self.query_data, name)
        chart = self.sps_chart if name == "sps" else getattr(self, "sps2_chart", None)
        # Ensure UI updates happen on UI thread
        self._apply_chart_update(chart, data_logs)

    def query_data(self, name: Literal['sps', 'sps2']):
        try:
            cnt = (
                DataLog.select(fn.COUNT(DataLog.id))
                .where(
                    (DataLog.utc_date_time >= self.start_date) &
                    (DataLog.utc_date_time <= self.end_date) &
                    (DataLog.name == name)
                ).scalar() or 0
            )
            logging.info(f"trendview query data count: {cnt}")
            max_data_count = 500
            portion = (cnt + max_data_count) // max_data_count
            logging.info(f"{name} trendview query data portion: {portion}")
            data_logs = (
                DataLog.select(
                    DataLog.power,
                    DataLog.speed,
                    DataLog.utc_date_time
                ).where(
                    (DataLog.utc_date_time >= self.start_date) &
                    (DataLog.utc_date_time <= self.end_date) &
                    (DataLog.name == name) &
                    (fn.MOD(DataLog.id, portion) == 0)
                ).order_by(DataLog.id.desc())
            )
            return list(data_logs)
        except:
            logging.exception('TrendView.query_data')
            return []
