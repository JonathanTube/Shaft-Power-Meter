import ctypes
import sys
import flet as ft
import asyncio
from common.const_alarm_type import AlarmType
from common.control_manager import ControlManager
from db.models.date_time_conf import DateTimeConf
from db.models.alarm_log import AlarmLog
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

# 加入开机启动
add_to_startup()

TableInit.init()
DataInit.init()

gdata.set_default_value()


def get_theme_mode():
    theme: Preference = Preference.get()
    return ft.ThemeMode.LIGHT if theme.theme == 0 else ft.ThemeMode.DARK


def load_language(page: ft.Page):
    language: Preference = Preference.get()
    language_items = Language.select()
    if language.language == 0:
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


async def handle_unexpected_exit():
    await asyncio.sleep(5)
    date_time_conf: DateTimeConf = DateTimeConf.get()
    # if the time diff is more than 5 seconds, send the alarm
    if abs((date_time_conf.system_date_time - gdata.system_date_time).total_seconds()) > 5:
        AlarmLog.create(utc_date_time=gdata.utc_date_time, alarm_type=AlarmType.APP_UNEXPECTED_EXIT)


async def main(page: ft.Page):
    TaskManager(page).start_all()

    asyncio.create_task(handle_unexpected_exit())

    load_language(page)

    page.title = page.session.get("lang.lang.app.name")
    page.padding = 0
    page.theme_mode = get_theme_mode()
    # page.window.full_screen = True
    # page.window.maximized = True
    page.window.resizable = False
    # page.window.title_bar_hidden = True
    page.window.width = 1024
    page.window.height = 768
    page.window.alignment = ft.alignment.center
    # page.window.always_on_top = False
    # page.window.frameless = True
    # page.window.maximizable = False

    # page.window.prevent_close = True
    ControlManager.fullscreen_alert = FullscreenAlert()
    ControlManager.audio_alarm = AudioAlarm()
    ControlManager.home = Home()

    page.theme = ft.Theme(scrollbar_theme=ft.ScrollbarTheme(thickness=20))

    main_content = ft.Container(expand=True, content=ControlManager.home, padding=0)

    page.appbar = Header(main_content)

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

if __name__ == "__main__":
    check_single_instance()
    ft.app(target=main)
