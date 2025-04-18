import ctypes
import sys
import flet as ft
import asyncio
from common.const_alarm_type import AlarmType
from db.models.date_time_conf import DateTimeConf
from db.models.alarm_log import AlarmLog
from ui.common.fullscreen_alert import FullscreenAlert
from ui.header.index import Header
from ui.home.index import Home
from task.breach_log_task import BreachLogTask
from task.gps_read_task import GpsReadTask
from task.plc_sync_task import PlcSyncTask
from task.modbus_read_task import ModbusReadTask
from task.data_save_task import DataSaveTask
from db.data_init import DataInit
from db.table_init import TableInit
from db.models.preference import Preference
from db.models.language import Language
from task.counter_total_task import CounterTotalTask
from task.counter_interval_task import CounterIntervalTask
from task.counter_manually_task import CounterManuallyTask
from task.test_mode_task import TestModeTask
from ui.common.audio_alarm import AudioAlarm
from task.utc_timer_task import utc_timer
from common.global_data import gdata


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
    asyncio.create_task(utc_timer.start())
    asyncio.create_task(CounterTotalTask(page).start())
    asyncio.create_task(CounterManuallyTask(page).start())
    asyncio.create_task(CounterIntervalTask(page).start())

    asyncio.create_task(PlcSyncTask(page).start())
    asyncio.create_task(ModbusReadTask(page).start())
    asyncio.create_task(DataSaveTask(page).start())
    asyncio.create_task(GpsReadTask(page).start())
    asyncio.create_task(BreachLogTask(page).start())


def add_file_picker(page: ft.Page):
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.session.set('file_picker_for_pdf_export', file_picker)


def check_single_instance(mutex_name: str = "shaft-power-meter"):
    # 创建互斥锁
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    last_error = ctypes.windll.kernel32.GetLastError()

    # 如果检测到已有实例，退出程序
    if last_error == 183:  # ERROR_ALREADY_EXISTS
        ctypes.windll.user32.MessageBoxW(
            0, "The Software is already running!", "Notice", 0x40)
        sys.exit(0)


async def handle_unexpected_exit():
    await asyncio.sleep(5)
    date_time_conf: DateTimeConf = DateTimeConf.get()
    # if the time diff is more than 5 seconds, send the alarm
    if abs((date_time_conf.system_date_time - utc_timer.get_utc_date_time()).total_seconds()) > 5:
        AlarmLog.create(
            utc_date_time=utc_timer.get_utc_date_time(),
            alarm_type=AlarmType.APP_UNEXPECTED_EXIT
        )
        gdata.alarm_occured = True


async def on_breach_alarm_occured(fullscreen_alert: FullscreenAlert, audio_alarm: AudioAlarm):
    while True:
        if gdata.breach_eexi_occured:
            audio_alarm.play()
            fullscreen_alert.start()
        else:
            audio_alarm.stop()
            fullscreen_alert.stop()
        await asyncio.sleep(1)


async def main(page: ft.Page):
    TableInit.init()
    DataInit.init()
    start_tasks(page)

    asyncio.create_task(handle_unexpected_exit())

    load_language(page)
    set_system_unit(page)

    add_file_picker(page)

    page.title = page.session.get("lang.lang.app.name")
    page.padding = 0
    page.theme_mode = get_theme_mode()
    # page.window.full_screen = True
    # page.window.maximized = True
    page.window.resizable = False
    page.window.width = 1024
    page.window.height = 768
    page.window.alignment = ft.alignment.center
    # page.window.always_on_top = False
    # page.window.frameless = True
    # page.window.title_bar_hidden = False
    # page.window.maximizable = False

    # page.window.prevent_close = True
    page.theme = ft.Theme(scrollbar_theme=ft.ScrollbarTheme(thickness=20))

    main_content = ft.Container(expand=True, content=Home(), padding=0)

    page.appbar = Header(main_content, TestModeTask(page))

    fullscreen_alert = FullscreenAlert()
    audio_alarm = AudioAlarm()

    main_stack = ft.Stack(
        [fullscreen_alert, main_content, audio_alarm], expand=True)

    page.add(main_stack)

    asyncio.create_task(on_breach_alarm_occured(fullscreen_alert, audio_alarm))

if __name__ == "__main__":
    check_single_instance()
    ft.app(target=main)
