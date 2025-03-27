import flet as ft
import asyncio

from ui.header.index import Header
from ui.home.index import Home
from utils.breach_log import BreachLogger
from utils.gps_logger import GpsLogger
from utils.data_logger import DataLogger
from db.data_init import DataInit
from db.table_init import TableInit


def start_loggers():
    gps_logger = GpsLogger()
    data_logger = DataLogger()
    breach_logger = BreachLogger()

    asyncio.create_task(gps_logger.start())
    asyncio.create_task(data_logger.start())
    asyncio.create_task(breach_logger.start())


def add_file_picker(page: ft.Page):
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.session.set('file_picker_for_pdf_export', file_picker)


async def main(page: ft.Page):
    TableInit.init()
    DataInit.init()
    start_loggers()
    add_file_picker(page)

    page.title = "Shaft Power Meter"
    page.padding = 0
    # page.theme_mode = ft.ThemeMode.LIGHT
    page.window.maximized = False
    page.window.resizable = False
    page.window.width = 1024
    page.window.height = 768
    page.window.alignment = ft.alignment.center
    page.window.always_on_top = False
    # page.window.frameless = True
    # page.window.title_bar_hidden = False
    page.window.maximizable = False

    # page.window.prevent_close = True

    page_content = ft.Container(expand=True, content=Home(), padding=0)

    page.appbar = Header(page_content)

    page.add(page_content)

ft.app(main)
