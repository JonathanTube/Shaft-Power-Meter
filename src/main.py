import asyncio
import ctypes
import sys
import logging
import ui_safety
import flet as ft
from task.task_manager import TaskManager
from ui.common.fullscreen_alert import FullscreenAlert
from ui.common.keyboard import keyboard
from ui.header.index import Header
from ui.home.index import Home
from ui.report.index import Report
from ui.setting.index import Setting
from db.data_init import DataInit
from db.table_init import TableInit
from db.models.language import Language
from ui.common.audio_alarm import AudioAlarm
from common.global_data import gdata
from task.modbus_output_task import modbus_output
from utils.auto_startup import add_to_startup
from utils.logger import Logger
from db.base import db
from task.gps_sync_task import gps
from task.plc_sync_task import plc
from task.utc_timer_task import utc_timer
from task.sps_read_task import sps_read_task
from task.sps2_read_task import sps2_read_task
from websocket.websocket_slave import ws_client
from websocket.websocket_master import ws_server
from task.data_record_task import data_record_task
from task.data_cleanup_task import data_cleanup_task

Logger(show_sql=False)
add_to_startup()


task_manager = TaskManager()


def check_single_instance(mutex_name: str = "shaft-power-meter"):
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    last_error = ctypes.windll.kernel32.GetLastError()
    if last_error == 183:
        ctypes.windll.user32.MessageBoxW(0, "The Software is already running!", "Notice", 0x40)
        sys.exit(0)


def load_language(page: ft.Page):
    language_items = Language.select()
    if gdata.configPreference.language == 0:
        for item in language_items:
            page.session.set(item.code, item.english)
    else:
        for item in language_items:
            page.session.set(item.code, item.chinese)


def set_appearance(page: ft.Page):
    page.theme = ft.Theme(scrollbar_theme=ft.ScrollbarTheme(thickness=20))
    page.title = page.session.get("lang.common.app_name")
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT if gdata.configPreference.theme == 0 else ft.ThemeMode.DARK
    page.window.resizable = False
    page.window.frameless = True
    page.window.left = 0
    page.window.top = 0
    if page.window.width <= 1200:
        if gdata.configPreference.fullscreen:
            page.window.full_screen = True
        else:
            page.window.maximized = True
    else:
        page.window.maximizable = False
        page.window.width = 1024
        page.window.height = 800
        page.window.resizable = False
    page.window.prevent_close = True


def set_content(page: ft.Page):
    content_home = Home()
    content_report = Report()
    content_setting = Setting()

    def change_main_menu(name: str):
        if name == 'HOME':
            content_home.current_index = 0
            main_content.content = content_home
        elif name == 'REPORT':
            main_content.content = content_report
        elif name == 'SETTING':
            content_setting.set_index_0()
            main_content.content = content_setting

        if main_content and main_content.page:
            main_content.update()

    page.appbar = Header(on_menu_click=change_main_menu)
    main_content = ft.Container(padding=0, margin=0, content=content_home)
    fullscreen_alert = FullscreenAlert()
    audio_alarm_btn = AudioAlarm()
    main_stack = ft.Stack(controls=[fullscreen_alert, main_content, audio_alarm_btn], expand=True)
    page.add(main_stack)

    async def watch_eexi_breach():
        is_running = False
        while True:
            try:
                if gdata.configCommon.is_eexi_breaching:
                    if not is_running:
                        fullscreen_alert.show()
                        await audio_alarm_btn.show()
                        is_running = True
                else:
                    if is_running:
                        fullscreen_alert.hide()
                        await audio_alarm_btn.hide()
                        is_running = False
            except Exception:
                logging.exception('watch_eexi_breach error')
            await asyncio.sleep(1)

    page.run_task(watch_eexi_breach)


async def start_all_tasks():
    # UTC 时钟
    await utc_timer.start()
    task_manager.add(utc_timer)

    # 数据清理
    await data_cleanup_task.start()
    task_manager.add(data_cleanup_task)

    # 数据记录
    await data_record_task.start()
    task_manager.add(data_record_task)

    # Modbus 输出
    await modbus_output.start()
    task_manager.add(modbus_output)

    # GPS
    if gdata.configCommon.enable_gps:
        await gps.start()
        task_manager.add(gps)

    # PLC
    if gdata.configCommon.is_master and gdata.configIO.plc_enabled:
        await plc.connect()
        task_manager.add(plc)

    # SPS 读取
    if gdata.configCommon.is_master:
        await sps_read_task.start()
        task_manager.add(sps_read_task)
        if gdata.configCommon.amount_of_propeller == 2:
            await sps2_read_task.start()
            task_manager.add(sps2_read_task)

    # WS
    if not gdata.configCommon.is_individual:
        await ws_server.start()
        task_manager.add(ws_server)
    else:
        await ws_client.start()
        task_manager.add(ws_client)


async def stop_all_tasks():
    await task_manager.stop_all()


async def main_async_setup(page: ft.Page):
    # initialize DB and defaults
    is_db_empty = len(db.get_tables()) == 0
    if is_db_empty:
        TableInit.init()
    DataInit.init()
    gdata.set_default_value()

    load_language(page)
    set_appearance(page)

    set_content(page)

    # start tasks AFTER UI ready
    await start_all_tasks()


async def main(page: ft.Page):
    ui_safety.init_ui_safety(page)

    page.overlay.append(keyboard)

    def handle_error(e):
        logging.error('global exception')
        logging.exception(e)

    try:
        page.on_error = handle_error
        await main_async_setup(page)
        page.on_close = lambda _: asyncio.create_task(stop_all_tasks())
    except Exception:
        logging.exception('exception in main')

if __name__ == "__main__":
    try:
        check_single_instance()
        ft.app(target=main)
    except Exception:
        logging.exception("fatal")
