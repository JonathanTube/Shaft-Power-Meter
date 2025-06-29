import flet as ft
import serial
import serial.tools.list_ports
import threading
import time
from queue import Queue


class ModbusFletApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Modbus RTU 上位机"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 800
        self.page.window_height = 600

        # 串口配置
        self.serial_port = None
        self.data_queue = Queue()
        self.is_connected = False
        self.polling_thread = None

        # 参数配置（32位寄存器映射）
        self.param_config = [
            {"name": "扭矩", "address": 0, "unit": "kN·m", "scale": 0.1},
            {"name": "推力", "address": 2, "unit": "kN", "scale": 0.1},
            {"name": "转速", "address": 4, "unit": "RPM", "scale": 0.1},
            {"name": "功率", "address": 6, "unit": "kW", "scale": 0.1},
            {"name": "平均功率", "address": 8, "unit": "kW", "scale": 0.1},
            {"name": "总能量", "address": 10, "unit": "kWh", "scale": 0.1}
        ]

        self.init_ui()
        self.start_polling()

    def init_ui(self):
        """构建用户界面"""
        # ===== 连接控制区 =====
        self.port_dropdown = ft.Dropdown(
            label="串口选择",
            options=self.get_serial_ports(),
            hint_text="选择串口设备"
        )

        self.refresh_btn = ft.ElevatedButton(
            "刷新端口",
            icon=ft.Icons.REFRESH,
            on_click=self.refresh_serial_ports
        )

        self.connect_btn = ft.ElevatedButton(
            "连接",
            icon=ft.Icons.USB,
            on_click=self.toggle_connection
        )

        self.status_text = ft.Text("状态: 未连接", color="red")

        # ===== 参数配置区 =====
        param_rows = []
        for param in self.param_config:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(param["name"])),
                    ft.DataCell(ft.Text(str(param["address"]))),
                    ft.DataCell(ft.Text(param["unit"])),
                    ft.DataCell(ft.Text(str(param["scale"]))),
                    ft.DataCell(ft.Text("0.0"))  # 当前值占位符
                ]
            )
            param_rows.append(row)

        self.param_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("参数名")),
                ft.DataColumn(ft.Text("寄存器地址")),
                ft.DataColumn(ft.Text("单位")),
                ft.DataColumn(ft.Text("缩放系数")),
                ft.DataColumn(ft.Text("当前值")),
            ],
            rows=param_rows
        )

        # ===== 实时数据区 =====
        data_rows = []
        for param in self.param_config:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(param["name"])),
                    ft.DataCell(ft.Text("0.0")),
                    ft.DataCell(ft.Text(param["unit"]))
                ]
            )
            data_rows.append(row)

        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("参数")),
                ft.DataColumn(ft.Text("值")),
                ft.DataColumn(ft.Text("单位")),
            ],
            rows=data_rows
        )

        # ===== 布局组装 =====
        self.page.add(
            ft.Row(
                controls=[
                    self.port_dropdown,
                    self.refresh_btn,
                    self.connect_btn,
                    self.status_text
                ],
                alignment=ft.MainAxisAlignment.START
            ),
            ft.Divider(height=20),
            ft.Text("实时数据:", weight=ft.FontWeight.BOLD),
            ft.Container(self.data_table, height=200)
        )

    def get_serial_ports(self):
        """获取系统可用串口列表"""
        ports = serial.tools.list_ports.comports()
        return [ft.dropdown.Option(key=port.name, text=f"{port.name} - {port.description}") for port in ports]

    def refresh_serial_ports(self, e):
        """刷新串口列表"""
        self.port_dropdown.options = self.get_serial_ports()
        self.page.update()

    def toggle_connection(self, e):
        """切换连接状态"""
        if self.is_connected:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        """建立串口连接"""
        port = self.port_dropdown.value
        if not port:
            return

        try:
            self.serial_port = serial.Serial(
                port=port,
                baudrate=9600,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=1
            )
            self.is_connected = True
            self.connect_btn.text = "断开"
            self.status_text.value = f"状态: 已连接 {port}"
            self.status_text.color = "green"
        except:
            pass

        self.page.update()

    def disconnect(self):
        """断开串口连接"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.is_connected = False
        self.connect_btn.text = "连接"
        self.status_text.value = "状态: 已断开"
        self.status_text.color = "red"
        self.page.update()

    def start_polling(self):
        """启动数据轮询线程"""
        def polling_task():
            while True:
                if self.is_connected and self.serial_port:
                    try:
                        # 读取所有参数（每个参数占2个寄存器）
                        for idx, param in enumerate(self.param_config):
                            # 构造Modbus RTU读取命令
                            slave_id = 1  # 默认从站ID
                            function_code = 3  # 读保持寄存器
                            start_addr = param["address"]
                            reg_count = 2  # 32位值需要2个寄存器

                            # 发送Modbus请求
                            cmd = bytearray([
                                slave_id,
                                function_code,
                                start_addr >> 8, start_addr & 0xFF,
                                reg_count >> 8, reg_count & 0xFF
                            ])

                            # 计算CRC校验
                            crc = self.calc_crc(cmd)
                            cmd.append(crc & 0xFF)
                            cmd.append(crc >> 8)

                            self.serial_port.write(cmd)

                            # 读取响应（5字节头 + 2*reg_count数据 + 2字节CRC）
                            response = self.serial_port.read(5 + 2*reg_count + 2)

                            if len(response) >= 7:
                                # 解析32位值（大端序）
                                high_byte = response[3]
                                low_byte = response[4]
                                high_reg = (high_byte << 8) | low_byte

                                high_byte = response[5]
                                low_byte = response[6]
                                low_reg = (high_byte << 8) | low_byte

                                # 组合32位整数
                                int_value = (high_reg << 16) | low_reg

                                # 处理有符号数
                                if int_value & 0x80000000:
                                    int_value -= 0x100000000

                                # 应用缩放系数
                                scaled_value = int_value * param["scale"]

                                # 更新UI
                                self.update_ui_value(idx, scaled_value)
                    except:
                        pass
                time.sleep(1)  # 1秒轮询间隔

        # 启动后台线程
        self.polling_thread = threading.Thread(target=polling_task, daemon=True)
        self.polling_thread.start()

    def update_ui_value(self, idx, value):
        """更新UI显示的值"""
        # 更新参数表
        self.param_table.rows[idx].cells[4].content.value = f"{value:.2f}"

        # 更新数据表
        self.data_table.rows[idx].cells[1].content.value = f"{value:.2f}"

        # 刷新页面
        self.page.update()

    def calc_crc(self, data):
        """计算Modbus CRC16校验码"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc


# def main(page: ft.Page):
#     app = ModbusFletApp(page)


# if __name__ == "__main__":
#     ft.app(target=main)
