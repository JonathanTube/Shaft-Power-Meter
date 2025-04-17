import socket
import flet as ft
from pymodbus.client import ModbusTcpClient

from db.models.io_conf import IOConf
from ui.common.custom_card import CustomCard
from ui.common.toast import Toast


class IO(ft.Container):
    def __init__(self):
        super().__init__()
        # ip v4 regex
        self.ipv4_regex = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
        # number regex
        self.reg_digital = r'^(\d+\.?\d*|)$'  # 允许整数、小数或空字符串
        self.last_io_conf = IOConf.get()

    def __create_plc_conf(self):
        self.plc_ip = ft.TextField(
            label=self.page.session.get("lang.setting.ip"), value=self.last_io_conf.plc_ip, col={'md': 4},
            # input_filter=ft.InputFilter(regex_string=self.ipv4_regex),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'plc_ip', e.control.value)
        )

        self.plc_port = ft.TextField(
            label=self.page.session.get("lang.setting.port"), value=self.last_io_conf.plc_port, col={'md': 4},
            input_filter=ft.NumbersOnlyInputFilter(),
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=5,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'plc_port', e.control.value)
        )

        self.power_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_power_min"),
            value=self.last_io_conf.power_range_min,
            suffix_text='kW',
            col={'md': 4},
            input_filter=ft.InputFilter(regex_string=self.reg_digital),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'power_range_min', e.control.value)
        )
        self.power_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_power_max"),
            value=self.last_io_conf.power_range_max,
            suffix_text='kW',
            col={'md': 4},
            input_filter=ft.InputFilter(regex_string=self.reg_digital),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'power_range_max', e.control.value)
        )
        self.power_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_power_offset"),
            value=self.last_io_conf.power_range_offset,
            suffix_text='kW',
            col={'md': 4},
            input_filter=ft.InputFilter(regex_string=self.reg_digital),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'power_range_offset', e.control.value)
        )

        self.torque_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_torque_min"),
            value=self.last_io_conf.torque_range_min,
            suffix_text='kNm',
            col={'md': 4},
            input_filter=ft.InputFilter(regex_string=self.reg_digital),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'torque_range_min', e.control.value)
        )
        self.torque_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_torque_max"),
            value=self.last_io_conf.torque_range_max,
            suffix_text='kNm',
            col={'md': 4},
            input_filter=ft.InputFilter(regex_string=self.reg_digital),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'torque_range_max', e.control.value)
        )
        self.torque_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_torque_offset"),
            value=self.last_io_conf.torque_range_offset,
            suffix_text='kNm',
            col={'md': 4},
            input_filter=ft.InputFilter(regex_string=self.reg_digital),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'torque_range_offset', e.control.value)
        )

        self.thrust_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_thrust_min"),
            value=self.last_io_conf.thrust_range_min,
            suffix_text='kN',
            col={'md': 4},
            input_filter=ft.InputFilter(regex_string=self.reg_digital),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'thrust_range_min', e.control.value)
        )
        self.thrust_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_thrust_max"),
            value=self.last_io_conf.thrust_range_max,
            suffix_text='kN',
            col={'md': 4},
            input_filter=ft.InputFilter(regex_string=self.reg_digital),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'thrust_range_max', e.control.value)
        )
        self.thrust_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_thrust_offset"),
            value=self.last_io_conf.thrust_range_offset,
            suffix_text='kN',
            col={'md': 4},
            input_filter=ft.InputFilter(regex_string=self.reg_digital),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'thrust_range_offset', e.control.value)
        )

        self.speed_range_min = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_speed_min"),
            value=self.last_io_conf.speed_range_min,
            suffix_text='rpm',
            col={'md': 4},
            input_filter=ft.InputFilter(regex_string=self.reg_digital),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'speed_range_min', e.control.value)
        )
        self.speed_range_max = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_speed_max"),
            value=self.last_io_conf.speed_range_max,
            suffix_text='rpm',
            col={'md': 4},
            input_filter=ft.InputFilter(regex_string=self.reg_digital),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'speed_range_max', e.control.value)
        )
        self.speed_range_offset = ft.TextField(
            label=self.page.session.get("lang.setting.4_20_ma_speed_offset"),
            value=self.last_io_conf.speed_range_offset,
            suffix_text='rpm',
            col={'md': 4},
            input_filter=ft.InputFilter(regex_string=self.reg_digital),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'speed_range_offset', e.control.value)
        )

        self.plc_conf = CustomCard(
            self.page.session.get("lang.setting.plc_conf"),    
            body=ft.ResponsiveRow(controls=[
                self.plc_ip,
                self.plc_port,
                # self.plc_conn_check,

                self.power_range_min,
                self.power_range_max,
                self.power_range_offset,

                self.torque_range_min,
                self.torque_range_max,
                self.torque_range_offset,

                self.thrust_range_min,
                self.thrust_range_max,
                self.thrust_range_offset,

                self.speed_range_min,
                self.speed_range_max,
                self.speed_range_offset,
            ]),
            col={"md": 12}
        )

    def __create_output_conf(self):
        self.check_torque = ft.Checkbox(
            label=self.page.session.get("lang.common.torque"),
            col={'md': 2},
            value=self.last_io_conf.output_torque,
            on_change=lambda e: setattr(self.last_io_conf, 'output_torque', e.control.value))

        self.check_thrust = ft.Checkbox(
            label=self.page.session.get("lang.common.thrust"),
            col={'md': 2},
            value=self.last_io_conf.output_thrust,
            on_change=lambda e: setattr(self.last_io_conf, 'output_thrust', e.control.value))

        self.check_power = ft.Checkbox(
            label=self.page.session.get("lang.common.power"),
            col={'md': 2},
            value=self.last_io_conf.output_power,
            on_change=lambda e: setattr(self.last_io_conf, 'output_power', e.control.value))

        self.check_speed = ft.Checkbox(
            label=self.page.session.get("lang.common.speed"),
            col={'md': 2},
            value=self.last_io_conf.output_speed,
            on_change=lambda e: setattr(self.last_io_conf, 'output_speed', e.control.value))

        self.check_avg_power = ft.Checkbox(
            label=self.page.session.get("lang.common.average_power"),
            col={'md': 2},
            value=self.last_io_conf.output_avg_power,
            on_change=lambda e: setattr(self.last_io_conf, 'output_avg_power', e.control.value))

        self.check_sum_power = ft.Checkbox(
            label=self.page.session.get("lang.common.sum_power"),
            col={'md': 2},
            value=self.last_io_conf.output_sum_power,
            on_change=lambda e: setattr(self.last_io_conf, 'output_sum_power', e.control.value))

        self.output_conf = CustomCard(
            self.page.session.get("lang.setting.output_conf"),
            body=ft.ResponsiveRow(
                controls=[
                    self.check_torque,
                    self.check_thrust,
                    self.check_power,
                    self.check_speed,
                    self.check_avg_power,
                    self.check_sum_power
                ]),
            col={"md": 12}
        )

    def __save_data(self, e):
        plc_client = None
        try:
            self.last_io_conf.save()
            plc_client = ModbusTcpClient(host=self.last_io_conf.plc_ip, port=self.last_io_conf.plc_port)
            plc_client.connect()
            plc_client.write_register(12298, int(self.last_io_conf.power_range_min))
            plc_client.write_register(12299, int(self.last_io_conf.power_range_max))
            plc_client.write_register(12300, int(self.last_io_conf.power_range_offset))

            plc_client.write_register(12308, int(self.last_io_conf.torque_range_min))
            plc_client.write_register(12309, int(self.last_io_conf.torque_range_max))
            plc_client.write_register(12310, int(self.last_io_conf.torque_range_offset))
            
            plc_client.write_register(12318, int(self.last_io_conf.thrust_range_min))
            plc_client.write_register(12319, int(self.last_io_conf.thrust_range_max))
            plc_client.write_register(12320, int(self.last_io_conf.thrust_range_offset))

            plc_client.write_register(12328, int(self.last_io_conf.speed_range_min))
            plc_client.write_register(12329, int(self.last_io_conf.speed_range_max))
            plc_client.write_register(12330, int(self.last_io_conf.speed_range_offset))
            Toast.show_success(e.page)
        except Exception as err:
            Toast.show_error(e.page, "lang.setting.save_limitations_to_plc_failed")
            print(err)
        finally:
            if plc_client:
                plc_client.close()

    def __reset_data(self, e):
        self.last_io_conf = IOConf.get()

        self.plc_ip.value = self.last_io_conf.plc_ip
        self.plc_port.value = self.last_io_conf.plc_port

        self.check_torque.value = self.last_io_conf.output_torque
        self.check_thrust.value = self.last_io_conf.output_thrust
        self.check_power.value = self.last_io_conf.output_power
        self.check_speed.value = self.last_io_conf.output_speed
        self.check_avg_power.value = self.last_io_conf.output_avg_power
        self.check_sum_power.value = self.last_io_conf.output_sum_power

        self.speed_range_min.value = self.last_io_conf.speed_range_min
        self.speed_range_max.value = self.last_io_conf.speed_range_max
        self.speed_range_offset.value = self.last_io_conf.speed_range_offset

        self.torque_range_min.value = self.last_io_conf.torque_range_min
        self.torque_range_max.value = self.last_io_conf.torque_range_max
        self.torque_range_offset.value = self.last_io_conf.torque_range_offset

        self.thrust_range_min.value = self.last_io_conf.thrust_range_min
        self.thrust_range_max.value = self.last_io_conf.thrust_range_max
        self.thrust_range_offset.value = self.last_io_conf.thrust_range_offset

        self.power_range_min.value = self.last_io_conf.power_range_min
        self.power_range_max.value = self.last_io_conf.power_range_max
        self.power_range_offset.value = self.last_io_conf.power_range_offset

        self.gps_ip.value = self.last_io_conf.gps_ip
        self.gps_port.value = self.last_io_conf.gps_port

        self.modbus_ip.value = self.last_io_conf.modbus_ip
        self.modbus_port.value = self.last_io_conf.modbus_port

        self.update()

        Toast.show_success(e.page)

    def __create_gps_conf(self):
        self.gps_ip = ft.TextField(
            label=self.page.session.get("lang.setting.ip"), value=self.last_io_conf.gps_ip, col={'md': 4},
            # input_filter=ft.InputFilter(regex_string=self.ipv4_regex),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'gps_ip', e.control.value)
        )

        self.gps_port = ft.TextField(
            label=self.page.session.get("lang.setting.port"), value=self.last_io_conf.gps_port, col={'md': 4},
            input_filter=ft.NumbersOnlyInputFilter(),
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=5,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'gps_port', e.control.value)
        )

        # self.gps_conn_check = ft.OutlinedButton(
        #     text="Check GPS Connection",
        #     expand=False,
        #     height=40,
        #     col={'md': 4},
        #     on_click=lambda e: self.check_ip_port(
        #         self.last_io_conf.gps_ip, self.last_io_conf.gps_port)
        # )
        self.gps_conf = CustomCard(
            self.page.session.get("lang.setting.gps_conf"),
            body=ft.ResponsiveRow(controls=[
                self.gps_ip,
                self.gps_port
                # self.gps_conn_check,
            ]),
            col={"md": 12}
        )

    def __create_modbus_conf(self):
        self.modbus_ip = ft.TextField(
            label=self.page.session.get("lang.setting.ip"), value=self.last_io_conf.modbus_ip, col={'md': 4},
            # input_filter=ft.InputFilter(regex_string=self.ipv4_regex),
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'modbus_ip', e.control.value)
        )
        self.modbus_port = ft.TextField(
            label=self.page.session.get("lang.setting.port"), value=self.last_io_conf.modbus_port, col={'md': 4},
            input_filter=ft.NumbersOnlyInputFilter(),
            max_length=5,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'modbus_port', e.control.value)
        )
        # self.modbus_conn_check = ft.OutlinedButton(
        #     text="Check Modbus Connection",
        #     expand=False,
        #     height=40,
        #     col={'md': 4},
        #     on_click=lambda e: self.check_ip_port(
        #         self.last_io_conf.modbus_ip, self.last_io_conf.modbus_port)
        # )
        self.modbus_conf = CustomCard(
            self.page.session.get("lang.setting.modbus_conf"),
            body=ft.ResponsiveRow(controls=[
                self.modbus_ip,
                self.modbus_port
                # self.modbus_conn_check,
            ]),
            col={"md": 12}
        )

    def build(self):
        self.__create_plc_conf()
        self.__create_output_conf()
        self.__create_gps_conf()
        self.__create_modbus_conf()

        self.save_button = ft.FilledButton(
            self.page.session.get("lang.button.save"), width=120, height=40, on_click=self.__save_data)
        self.reset_button = ft.OutlinedButton(
            self.page.session.get("lang.button.reset"), width=120, height=40, on_click=self.__reset_data)

        self.content = ft.Column(
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
            controls=[
                ft.ResponsiveRow(
                    controls=[
                        self.plc_conf,
                        self.gps_conf,
                        self.modbus_conf,
                        self.output_conf,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                self.save_button,
                                self.reset_button
                            ]
                        )
                    ]
                )
            ]
        )