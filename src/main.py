import flet as ft
import asyncio

from ui.header.index import Header
from ui.home.index import Home
from task.utc_timer_task import UtcTimer
from task.breach_log_task import BreachLogTask
from task.gps_read_task import GpsReadTask
from task.plc_read_task import PlcReadTask
from task.modbus_read_task import ModbusReadTask
from task.data_save_task import DataSaveTask
from db.data_init import DataInit
from db.table_init import TableInit
from db.models.preference import Preference
from db.models.language import Language
from task.counter_total_task import CounterTotalTask
from task.counter_interval_task import CounterIntervalTask
from task.counter_manually_task import CounterManuallyTask


def get_theme_mode():
    theme = Preference.get().theme
    if theme == 0:
        return ft.ThemeMode.SYSTEM
    elif theme == 1:
        return ft.ThemeMode.LIGHT
    elif theme == 2:
        return ft.ThemeMode.DARK


def load_language(page: ft.Page):
    language = Preference.get().language
    language_items = Language.select()
    if language == 0:
        for item in language_items:
            page.session.set(item.code, item.english)
    elif language == 1:
        for item in language_items:
            page.session.set(item.code, item.chinese)


def set_system_unit(page: ft.Page):
    system_unit = Preference.get().system_unit
    page.session.set('system_unit', system_unit)


def start_tasks(page: ft.Page):
    asyncio.create_task(UtcTimer(page).start())

    asyncio.create_task(CounterTotalTask(page).start())
    asyncio.create_task(CounterManuallyTask(page).start())
    asyncio.create_task(CounterIntervalTask(page).start())

    asyncio.create_task(GpsReadTask(page).start())
    asyncio.create_task(PlcReadTask(page).start())
    asyncio.create_task(ModbusReadTask(page).start())
    asyncio.create_task(DataSaveTask(page).start())
    
    asyncio.create_task(BreachLogTask(page).start())


def add_file_picker(page: ft.Page):
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.session.set('file_picker_for_pdf_export', file_picker)


async def main(page: ft.Page):
    TableInit.init()
    DataInit.init()
    start_tasks(page)

    load_language(page)
    set_system_unit(page)

    add_file_picker(page)

    page.title = page.session.get("lang.lang.app.name")
    page.padding = 0
    page.theme_mode = get_theme_mode()
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

    main_content = ft.Container(
        expand=True,
        content=Home(),
        padding=0
    )

    page.appbar = Header(main_content)

    page.add(main_content)


ft.app(main)
