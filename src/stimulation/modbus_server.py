import flet as ft
from pymodbus.server import StartAsyncSerialServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
import asyncio
import numpy as np
import serial.tools.list_ports


class modbus_server(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 10
        self.thrust = 2500  # 初始推力值 (N)
        self.torque = 80    # 初始扭力值 (N·m)

        self._task = None
        self.port = None

    def build(self):
        options = [
            ft.dropdown.Option(
                key=port.name,
                text=f"{port.name} - {port.description}"
            )
            for port in serial.tools.list_ports.comports()
        ]

        dropdown = ft.Dropdown(
            expand=True,
            color=ft.Colors.GREEN_500,
            label="Port",
            options=options,
            on_change=self.__on_select_change
        )

        self.list_view = ft.ListView(
            auto_scroll=True,
            height=500,
            expand=True
        )

        self.operations = ft.Row(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                dropdown,
                ft.FilledButton(
                    text="Connect",
                    bgcolor=ft.Colors.GREEN_500,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: self.__connect()
                ),
                ft.FilledButton(
                    text="Disconnect",
                    bgcolor=ft.Colors.RED_500,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: self.__disconnect()
                ),
                ft.FilledButton(
                    text="Send Data",
                    bgcolor=ft.Colors.BLUE_500,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: self.__send_data()
                )
            ]
        )

        self.content = ft.Column(
            expand=True,
            controls=[
                self.operations,
                self.list_view
            ]
        )

    def __generate_data(self):
        """生成带随机波动的数据"""
        self.thrust += np.random.uniform(-50, 50)
        self.thrust = np.clip(self.thrust, 0, 5000)

        self.torque += np.random.uniform(-5, 5)
        self.torque = np.clip(self.torque, -100, 100)
        return int(self.thrust), int(self.torque)

    def __send_data(self):
        self._task = self.page.run_task(self.__output_data)

    def __disconnect(self):
        pass
        # if self.server:
        #     self.server.close()
        #     self.server = None
        #     self._task = None
        #     self.port = None

    async def __output_data(self):
        while True:
            thrust, torque = self.__generate_data()
            print(f"更新寄存器: 推力={thrust}N, 扭力={torque}Nm")
            self.context[0].setValues(3, 0, [thrust])  # 3=Holding Register
            self.context[0].setValues(3, 1, [torque])
            await asyncio.sleep(1)

    def __connect(self):
        self.page.run_task(self.__start_modbus_server)

    async def __start_modbus_server(self):
        # 初始化数据存储
        data_block = ModbusSequentialDataBlock(0, [0]*2)  # 地址0开始，初始化2个寄存器
        store = ModbusSlaveContext(hr=data_block)
        self.context = ModbusServerContext(slaves=store, single=True)

        # 启动Modbus RTU服务
        await StartAsyncSerialServer(
            context=self.context,
            port=self.port,
            baudrate=115200,
            stopbits=1,
            bytesize=8,
            parity='N'
        )

    def __on_select_change(self, e):
        self.port = e.control.value
