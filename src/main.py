import flet as ft
import asyncio

from db.base import db
from db.models.breach_reason import BreachReason
from db.models.zero_cal_info import ZeroCalInfo
from db.models.zero_cal_record import ZeroCalRecord
from ui.header.index import Header
from ui.home.index import Home
from utils.breach_log import BreachLogger
from utils.gps_logger import GpsLogger
from utils.data_logger import DataLogger


def init_db():
    # db.drop_tables([DataLog, BreachLog], safe=False)
    db.create_tables([ZeroCalInfo, ZeroCalRecord], safe=True)


def init_data():
    if BreachReason.select().count() == 0:
        BreachReason.insert_many([
            {"reason": "operating in adverse weather"},
            {"reason": "opearting in ice-infested waters"},
            {"reason": "participation in search and rescue operations"},
            {"reason": "avoidance of porates"},
            {"reason": "engine maintenance"},
            {"reason": "description of other reasons"}
        ]).execute()


def start_loggers():
    gps_logger = GpsLogger()
    data_logger = DataLogger()
    breach_logger = BreachLogger()

    asyncio.create_task(gps_logger.start())
    asyncio.create_task(data_logger.start())
    asyncio.create_task(breach_logger.start())


async def main(page: ft.Page):
    init_db()
    init_data()
    # start_loggers()

    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.maximized = True
    page.window.resizable = False
    page.window.max_width = 1024
    page.window.max_height = 768
    page.window.frameless = True
    page.padding = 0
    # page.window.prevent_close = True

    page_content = ft.Container(expand=True, content=Home(), padding=0)

    page.appbar = Header(page_content)

    page.add(page_content)
    print('page.window.width=', page.window.width)
    print('page.width=', page.width)


ft.app(main)
