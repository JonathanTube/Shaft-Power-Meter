import serial
import time
import random
import serial.tools.list_ports
import flet as ft
import asyncio
from datetime import datetime


class gps_server(ft.Container):
    def __init__(self):
        super().__init__()
        self.padding = 10
        self.expand = True
        self.ser = None
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

    def __on_select_change(self, e):
        self.port = e.control.value

    def __generate_nmea_0183(self):
        """生成模拟的NMEA 0183 GPRMC语句"""

        timestamp = time.strftime("%H%M%S", time.gmtime())
        latitude = f"{random.uniform(0, 90):07.3f}"  # 随机纬度
        ns = 'N' if random.random() > 0.5 else 'S'
        longitude = f"{random.uniform(0, 180):07.3f}"  # 随机经度
        ew = 'E' if random.random() > 0.5 else 'W'
        speed = f"{random.uniform(0, 50):05.1f}"      # 随机速度（节）
        course = f"{random.uniform(0, 360):05.1f}"    # 随机航向
        date = time.strftime("%d%m%y", time.gmtime())
        variation = "003.1,W"  # 磁偏角

        # 构造语句
        nmea_format = (
            f"GPRMC,{timestamp},A,{latitude},{ns},{longitude},{ew},"
            f"{speed},{course},{date},{variation}"
        )

        # 计算校验和（$和*之间的字符异或）
        checksum = 0
        for char in nmea_format:
            checksum ^= ord(char)

        return f"${nmea_format}*{checksum:02X}"

    def __disconnect(self):
        if self._task:
            self._task.cancel()
            self._task = None

        if self.ser and self.ser.is_open:
            old_port = self.ser.port
            self.ser.close()
            self.list_view.controls.append(
                ft.Text(f"Serial port {old_port} was closed", color=ft.Colors.RED, weight=ft.FontWeight.BOLD))
            self.list_view.update()

    def __connect(self):
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=4800,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            # self.ser.open()

            if self.ser.is_open:
                self.list_view.controls.append(
                    ft.Text(f"Serial port {self.port} has been opened", color=ft.Colors.GREEN_500, weight=ft.FontWeight.BOLD))
                self.list_view.update()
            else:
                self.list_view.controls.append(
                    ft.Text(f"Serial port {self.port} wasn't opened", color=ft.Colors.RED, weight=ft.FontWeight.BOLD))
                self.list_view.update()

        except serial.SerialException as e:
            self.list_view.controls.append(
                ft.Text(f"Error: {e}", color=ft.Colors.RED, weight=ft.FontWeight.BOLD))
            self.list_view.update()

    def __send_data(self):
        if self.ser and self.ser.is_open:
            self._task = self.page.run_task(self.__output_data)
        else:
            self.list_view.controls.append(
                ft.Text(f"Serial port {self.port} wasn't opened", color=ft.Colors.RED, weight=ft.FontWeight.BOLD))
            self.list_view.update()

    async def __output_data(self):
        try:
            while True:
                # 生成并发送数据
                sentence = self.__generate_nmea_0183() + "\r\n"  # 加上NMEA结束符
                self.list_view.controls.append(
                    ft.Text(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}: {sentence.strip()}', color=ft.Colors.GREEN_500))
                self.list_view.update()
                # self.ser.write(sentence.encode('utf-8'))
                print(f"Sent: {sentence.strip()}")
                # 每秒发送一次
                await asyncio.sleep(1)
        except Exception as e:
            dlg = ft.AlertDialog(
                title=ft.Text("Error"),
                content=ft.Text(f"Error: {e}"),
                actions=[
                    ft.TextButton(
                        text="OK",
                        on_click=lambda e: self.page.close(dlg)
                    )
                ]
            )
            self.page.open(dlg)
        finally:
            self.ser.close()
            print("Serial port closed")
