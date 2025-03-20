import flet as ft
import asyncio

from db.base import db
from db.models.breach_reason import BreachReason
from db.models.counter_log import CounterLog
from db.models.data_log import DataLog
from db.models.date_time_conf import DateTimeConf
from db.models.event_log import EventLog
from db.models.factor_conf import FactorConf
from db.models.gps_log import GpsLog
from db.models.io_conf import IOConf
from db.models.limitations import Limitations
from db.models.preference import Preference
from db.models.propeller_setting import PropellerSetting
from db.models.report_detail import ReportDetail
from db.models.report_info import ReportInfo
from db.models.ship_info import ShipInfo
from db.models.system_settings import SystemSettings
from db.models.zero_cal_info import ZeroCalInfo
from db.models.zero_cal_record import ZeroCalRecord
from ui.header.index import Header
from ui.home.index import Home
from utils.breach_log import BreachLogger
from utils.gps_logger import GpsLogger
from utils.data_logger import DataLogger


def init_tables():
    # db.drop_tables([DataLog, BreachLog], safe=False)
    db.create_tables([
        BreachReason,
        CounterLog,
        DataLog,
        DateTimeConf,
        EventLog,
        FactorConf,
        GpsLog,
        IOConf,
        Limitations,
        Preference,
        PropellerSetting,
        ReportDetail,
        ReportInfo,
        ShipInfo,
        SystemSettings,
        ZeroCalInfo,
        ZeroCalRecord
    ], safe=True)


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


def init_test_data():
    if ReportInfo.select().count() == 0:
        ReportInfo.insert_many([
            {"report_name": "Test Report 1"},
            {"report_name": "Test Report 2"},
            {"report_name": "Test Report 3"},
            {"report_name": "Test Report 4"},
            {"report_name": "Test Report 5"},
            {"report_name": "Test Report 6"},
            {"report_name": "Test Report 7"},
            {"report_name": "Test Report 8"},
            {"report_name": "Test Report 9"},
            {"report_name": "Test Report 10"}
        ]).execute()


def start_loggers():
    gps_logger = GpsLogger()
    data_logger = DataLogger()
    breach_logger = BreachLogger()

    asyncio.create_task(gps_logger.start())
    asyncio.create_task(data_logger.start())
    asyncio.create_task(breach_logger.start())

def add_file_picker(page:ft.Page):
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    page.session.set('file_picker_for_pdf_export',file_picker)

async def main(page: ft.Page):
    init_tables()
    init_data()
    init_test_data()
    # start_loggers()
    add_file_picker(page)

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
