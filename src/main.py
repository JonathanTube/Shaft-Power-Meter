import asyncio
import ctypes
import sys
import logging
import flet as ft
from db.models.system_settings import SystemSettings
from task.utc_timer_task import UtcTimer
from ui.common.fullscreen_alert import FullscreenAlert
from ui.common.keyboard import keyboard
from ui.common.windows_sound_player import WindowsSoundPlayer
from ui.header.index import Header
from ui.home.index import Home
from ui.report.index import Report
from ui.setting.index import Setting
from db.data_init import DataInit
from db.table_init import TableInit
from db.models.preference import Preference
from db.models.language import Language
from ui.common.audio_alarm import AudioAlarm
from common.global_data import gdata
from utils.modbus_output import modbus_output
from utils.auto_startup import add_to_startup
from utils.logger import Logger
from db.base import db
from task.gps_sync_task import gps_sync_task
from task.sps_offline_task import sps_offline_task
from task.utc_timer_task import UtcTimer
from task.sps1_read_task import sps1_read_task
from task.sps2_read_task import sps2_read_task
from utils.plc_util import plc_util
from websocket.websocket_server import ws_server
from websocket.websocket_client import ws_client


Logger(show_sql=False)

# 加入开机启动
add_to_startup()


is_db_empty = len(db.get_tables()) == 0
if is_db_empty:
    TableInit.init()
    DataInit.init()

gdata.set_default_value()

sound_player = WindowsSoundPlayer()


def get_theme_mode(preference: Preference):
    # theme: Preference = Preference.get()
    return ft.ThemeMode.LIGHT if preference.theme == 0 else ft.ThemeMode.DARK


def load_language(page: ft.Page, preference: Preference):
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


def start_all_task():
    system_settings: SystemSettings = SystemSettings.get()
    asyncio.create_task(UtcTimer().start())
    asyncio.create_task(sps_offline_task.start())

    # 如果不是第一次装机，启动设备连接
    if not is_db_empty:
        # GSP 不管主机从机都有
        asyncio.create_task(gps_sync_task.start())
        asyncio.create_task(modbus_output.start())

        # 如果是主机
        if system_settings.is_master:
            asyncio.create_task(plc_util.auto_reconnect())
            asyncio.create_task(sps1_read_task.start())
            asyncio.create_task(ws_server.start())
            # start sps2 JM3846 if dual propellers.
            if system_settings.amount_of_propeller > 1:
                asyncio.create_task(sps2_read_task.start())
        else:
            # 从机只需要启动，客户端
            asyncio.create_task(ws_client.start())


def set_appearance(page: ft.Page, preference: Preference):
    page.theme = ft.Theme(scrollbar_theme=ft.ScrollbarTheme(thickness=20))
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


def on_mute():
    sound_player.stop()


def set_content(page: ft.Page):
    page.appbar = Header()

    main_content = ft.Container(padding=0, margin=0, content=Home())

    fullscreen_alert = FullscreenAlert()

    audio_alarm_btn = AudioAlarm(on_mute=on_mute)

    main_stack = ft.Stack(
        controls=[
            fullscreen_alert,
            main_content,
            audio_alarm_btn
        ],
        expand=True
    )
    page.add(main_stack)
    page.overlay.append(keyboard)

    # 主菜单切换
    def change_main_menu(topic, message):
        if message == 'HOME':
            main_content.content = Home()
        elif message == 'REPORT':
            main_content.content = Report()
        elif message == 'SETTING':
            main_content.content = Setting()
        main_content.update()

    page.pubsub.subscribe_topic('__change_main_menu', change_main_menu)

    # 监听EEXI breach

    async def watch_eexi_breach():
        is_running = False
        while True:
            try:
                if gdata.eexi_breach:
                    if not is_running:
                        fullscreen_alert.show()
                        audio_alarm_btn.show()
                        sound_player.play()
                        is_running = True
                else:
                    if is_running:
                        fullscreen_alert.hide()
                        audio_alarm_btn.hide()
                        sound_player.stop()
                        is_running = False
            except:
                logging.exception('exception occured at FullscreenAlert.__watch_eexi_breach')
            finally:
                await asyncio.sleep(1)

    page.run_task(watch_eexi_breach)


async def main(page: ft.Page):
    try:
        preference: Preference = Preference.get()

        load_language(page, preference)
        set_appearance(page, preference)

        page.on_error = handle_error

        set_content(page)

        page.update()

        start_all_task()

    except:
        logging.exception('exception occured at main')

if __name__ == "__main__":
    check_single_instance()
    ft.app(target=main)
