import ctypes
import os
from pathlib import Path
import sys
import flet as ft
from common.control_manager import ControlManager
from ui.common.fullscreen_alert import FullscreenAlert
from ui.common.keyboard import keyboard
from ui.header.index import Header
from ui.home.index import Home
from db.data_init import DataInit
from db.table_init import TableInit
from db.models.preference import Preference
from db.models.language import Language
from ui.common.audio_alarm import AudioAlarm
from task.task_manager import TaskManager
from common.global_data import gdata
from utils.auto_startup import add_to_startup
from utils.logger import Logger
from utils.modbus_output import modbus_output
from db.base import db
import logging

Logger(show_sql=False)

# 加入开机启动
add_to_startup()


is_db_empty = len(db.get_tables()) == 0
if is_db_empty:
    TableInit.init()
    DataInit.init()

gdata.set_default_value()


def get_theme_mode(preference : Preference):
    # theme: Preference = Preference.get()
    return ft.ThemeMode.LIGHT if preference.theme == 0 else ft.ThemeMode.DARK


def load_language(page: ft.Page, preference : Preference):
    # language: Preference = Preference.get()
    language_items = Language.select()
    if preference.language == 0:
        for item in language_items:
            page.session.set(item.code, item.english)
    else:
        for item in language_items:
            page.session.set(item.code, item.chinese)


def check_single_instance(mutex_name: str = "shaft-power-meter"):
    # 创建互斥锁
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    last_error = ctypes.windll.kernel32.GetLastError()

    # 如果检测到已有实例，退出程序
    if last_error == 183:  # ERROR_ALREADY_EXISTS
        ctypes.windll.user32.MessageBoxW(0, "The Software is already running!", "Notice", 0x40)
        sys.exit(0)

def handle_error(e):
    logging.error('============global exception occured===========')
    logging.exception(e)

def init_audio(page:ft.Page) -> ft.Audio:
    # create audio alarm
    src = os.path.join(Path(__file__).parent,"assets","TF001.WAV")
    logging.info(src)
    audio = ft.Audio(src=src, autoplay=False, release_mode=ft.audio.ReleaseMode.LOOP)
    page.overlay.append(audio)
    return audio

async def main(page: ft.Page):
    try:
        preference: Preference = Preference.get()

        load_language(page, preference)

        await modbus_output.start_modbus_server()

        page.on_error = handle_error

        page.title = page.session.get("lang.lang.app.name")
        page.padding = 0
        page.theme_mode = get_theme_mode(preference)
        page.window.resizable = False
        page.window.alignment = ft.alignment.center
        page.window.frameless = True
        page.window.always_on_top = False
        page.window.alignment = ft.alignment.center
        if page.window.width <= 1200:
            if preference.fullscreen:
                page.window.full_screen = True
            else:
                page.window.maximized = True
        else:
            page.window.maximizable = False
            page.window.width = 1024
            page.window.height = 800
            page.window.resizable = False
        page.window.prevent_close = True
        ControlManager.fullscreen_alert = FullscreenAlert()
        logging.info('add fullscreen alert')

        audio : ft.Audio = init_audio(page)
        ControlManager.audio_alarm = AudioAlarm(audio)
        logging.info('add audio alert')
        ControlManager.home = Home()

        page.theme = ft.Theme(scrollbar_theme=ft.ScrollbarTheme(thickness=20))

        main_content = ft.Container(expand=True, content=ControlManager.home, padding=0)

        header:Header = Header(main_content)
        ControlManager.app_bar = header
        page.appbar = header

        main_stack = ft.Stack(
            controls=[
                ControlManager.fullscreen_alert,
                main_content,
                ControlManager.audio_alarm
            ],
            expand=True
        )

        page.add(main_stack)

        page.overlay.append(keyboard)

        page.update()

        TaskManager().start_all(is_db_empty)
    except:
        logging.exception('exception occured at main')

if __name__ == "__main__":
    check_single_instance()
    ft.app(target=main)
    
