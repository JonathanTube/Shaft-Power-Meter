import flet as ft
from common.const_pubsub_topic import PubSubTopic
from common.global_data import gdata

class SelfTest(ft.Tabs):
    def __init__(self):
        super().__init__()

    def build(self):
        self.plc_log = ft.ListView(
            padding=10,
            auto_scroll=True,
            height=500,
            spacing=5,
            expand=True
        )
        self.modbus_log = ft.ListView(
            padding=10,
            auto_scroll=True,
            height=500,
            spacing=5,
            expand=True
        )
        self.gps_log = ft.ListView(
            padding=10,
            auto_scroll=True,
            height=500,
            spacing=5,
            expand=True
        )
        self.tabs = [
            ft.Tab(text="PLC Connection", content=self.plc_log),
            ft.Tab(text="Modbus RTU 485", content=self.modbus_log),
            ft.Tab(text="GPS RS232", content=self.gps_log)
        ]

    async def __read_plc_data(self, topic, message):
        utc_date_time = gdata.utc_date_time
        content = f"{utc_date_time}: {message}"
        self.plc_log.controls.append(ft.Text(content))
        self.plc_log.update()

    async def __read_modbus_data(self, topic, message):
        utc_date_time = gdata.utc_date_time
        content = f"{utc_date_time}: {message}"
        self.modbus_log.controls.append(ft.Text(content))
        self.modbus_log.update()

    async def __read_gps_log(self, topic, message):
        utc_date_time = gdata.utc_date_time
        content = f"{utc_date_time}: {message}"
        self.gps_log.controls.append(ft.Text(content))
        self.gps_log.update()

    def did_mount(self):
        pubsub = self.page.pubsub

        pubsub.subscribe_topic(
            PubSubTopic.TRACE_PLC_LOG,
            self.__read_plc_data
        )

        pubsub.subscribe_topic(
            PubSubTopic.TRACE_MODBUS_LOG,
            self.__read_modbus_data
        )

        pubsub.subscribe_topic(
            PubSubTopic.TRACE_GPS_LOG,
            self.__read_gps_log
        )

    def will_unmount(self):
        pubsub = self.page.pubsub
        pubsub.unsubscribe_topic(PubSubTopic.TRACE_PLC_LOG)
        pubsub.unsubscribe_topic(PubSubTopic.TRACE_MODBUS_LOG)
        pubsub.unsubscribe_topic(PubSubTopic.TRACE_GPS_LOG)
