import os
from pathlib import Path
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


def create_audio_alarm(page: ft.Page):
    # create audio alarm
    audit_src = os.path.join(Path(__file__).parent, "assets", "alarm.mp3")
    print(audit_src)
    audio_alarm = ft.Audio(src=audit_src, autoplay=False,
                           release_mode=ft.audio.ReleaseMode.LOOP)
    page.overlay.append(audio_alarm)
    return audio_alarm


def create_override_button(audio_alarm: ft.Audio):
    def on_override_button_click(e):
        audio_alarm.pause()
        override_button.icon = ft.Icons.NOTIFICATIONS_OFF_OUTLINED
        override_button.disabled = True
        override_button.bgcolor = ft.Colors.RED_400
        override_button.update()

    override_button = ft.FilledButton(
        top=8,
        right=20,
        text="Override",
        icon=ft.Icons.NOTIFICATIONS_ON_OUTLINED,
        icon_color=ft.Colors.WHITE,
        bgcolor=ft.Colors.RED,
        color=ft.Colors.WHITE,
        visible=False,
        on_click=on_override_button_click
    )
    return override_button


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

    main_content = ft.Container(expand=True, content=Home(), padding=0)

    page.appbar = Header(main_content)

    audio_alarm = create_audio_alarm(page)
    override_button = create_override_button(audio_alarm)

    main_stack = ft.Stack([main_content, override_button], expand=True)

    def on_breach_alarm_occured(topic, occured):
        if occured:
            override_button.icon = ft.icons.NOTIFICATIONS_ON_OUTLINED
            override_button.bgcolor = ft.Colors.RED
            override_button.visible = True
            override_button.disabled = False
            audio_alarm.play()
        else:
            override_button.visible = False
            audio_alarm.pause()
        override_button.update()
    page.pubsub.subscribe_topic("breach_alarm_occured", on_breach_alarm_occured)
    page.add(main_stack)

ft.app(main)
