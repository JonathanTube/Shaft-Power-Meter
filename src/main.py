import flet as ft
import asyncio

from db.base import db
from db.models.zero_cal_info import ZeroCalInfo
from db.models.zero_cal_record import ZeroCalRecord
from ui.header.index import Header
from ui.home.index import create_home
from utils.gps_logger import GpsLogger


async def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page_content = ft.Container(expand=True)

    page.window.maximized = True
    page.window.resizable = False
    page.window.max_width = 1024
    page.window.max_height = 768
    page.window.frameless = True
    # page.window.prevent_close = True

    page.appbar = Header(page_content)

    page_content.content = create_home()

    page.padding = ft.padding.only(left=0, right=0, top=0, bottom=0)

    page.add(page_content)
    print('page.window.width=', page.window.width)
    print('page.width=', page.width)

    # Start GPS logger
    gps_logger = GpsLogger()
    asyncio.create_task(gps_logger.start())


db.create_tables([ZeroCalInfo, ZeroCalRecord], safe=True)

ft.app(main)
