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
            label="IP", value=self.last_io_conf.plc_ip, col={'md': 4},
            # input_filter=ft.InputFilter(regex_string=self.ipv4_regex),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'plc_ip', e.control.value)
        )

        self.plc_port = ft.TextField(
            label="Port", value=self.last_io_conf.plc_port, col={'md': 4},
            input_filter=ft.NumbersOnlyInputFilter(),
            keyboard_type=ft.KeyboardType.NUMBER,
            max_length=5,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'plc_port', e.control.value)
        )

        self.power_range_min = ft.TextField(
            label="4-20MA Power Min",
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
            label="4-20MA Power Max",
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
            label="4-20MA Power Offset",
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
            label="4-20MA Torque Min",
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
            label="4-20MA Torque Max",
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
            label="4-20MA Torque Offset",
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
            label="4-20MA Thrust Min",
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
            label="4-20MA Thrust Max",
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
            label="4-20MA Thrust Offset",
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
            label="4-20MA Speed Min",
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
            label="4-20MA Speed Max",
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
            label="4-20MA Speed Offset",
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
            'PLC Conf.',
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
            label="Torque(kNm)",
            col={'md': 2},
            value=self.last_io_conf.output_torque,
            on_change=lambda e: setattr(self.last_io_conf, 'output_torque', e.control.value))

        self.check_thrust = ft.Checkbox(
            label="Thrust(kN)",
            col={'md': 2},
            value=self.last_io_conf.output_thrust,
            on_change=lambda e: setattr(self.last_io_conf, 'output_thrust', e.control.value))

        self.check_power = ft.Checkbox(
            label="Power(kw)",
            col={'md': 2},
            value=self.last_io_conf.output_power,
            on_change=lambda e: setattr(self.last_io_conf, 'output_power', e.control.value))

        self.check_speed = ft.Checkbox(
            label="Speed(rpm)",
            col={'md': 2},
            value=self.last_io_conf.output_speed,
            on_change=lambda e: setattr(self.last_io_conf, 'output_speed', e.control.value))

        self.check_avg_power = ft.Checkbox(
            label="Average Power(kw)",
            col={'md': 2},
            value=self.last_io_conf.output_avg_power,
            on_change=lambda e: setattr(self.last_io_conf, 'output_avg_power', e.control.value))

        self.check_sum_power = ft.Checkbox(
            label="Sum Of Power(kwh)",
            col={'md': 2},
            value=self.last_io_conf.output_sum_power,
            on_change=lambda e: setattr(self.last_io_conf, 'output_sum_power', e.control.value))

        self.output_conf = CustomCard(
            'Output Conf.',
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
            label="IP", value=self.last_io_conf.gps_ip, col={'md': 4},
            # input_filter=ft.InputFilter(regex_string=self.ipv4_regex),
            keyboard_type=ft.KeyboardType.NUMBER,
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'gps_ip', e.control.value)
        )

        self.gps_port = ft.TextField(
            label="Port", value=self.last_io_conf.gps_port, col={'md': 4},
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
            'GPS Conf.',
            body=ft.ResponsiveRow(controls=[
                self.gps_ip,
                self.gps_port
                # self.gps_conn_check,
            ]),
            col={"md": 12}
        )

    def __create_modbus_conf(self):
        self.modbus_ip = ft.TextField(
            label="IP", value=self.last_io_conf.modbus_ip, col={'md': 4},
            # input_filter=ft.InputFilter(regex_string=self.ipv4_regex),
            size_constraints=ft.BoxConstraints(max_height=40),
            text_size=14,
            on_change=lambda e: setattr(
                self.last_io_conf, 'modbus_ip', e.control.value)
        )
        self.modbus_port = ft.TextField(
            label="Port", value=self.last_io_conf.modbus_port, col={'md': 4},
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
            'Modbus Conf.',
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
            text="Save", width=120, height=40, on_click=self.__save_data)
        self.reset_button = ft.OutlinedButton(
            text="Reset", width=120, height=40, on_click=self.__reset_data)

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

    def __set_language(self):
        session = self.page.session
        self.plc_conf.set_title(session.get("lang.setting.plc_conf"))
        self.plc_ip.label = session.get("lang.setting.ip")
        self.plc_port.label = session.get("lang.setting.port")
        # self.plc_conn_check.text = session.get("lang.setting.check_plc_connection")

        self.power_range_min.label = session.get("lang.setting.4_20_ma_power_min")
        self.power_range_max.label = session.get("lang.setting.4_20_ma_power_max")
        self.power_range_offset.label = session.get("lang.setting.4_20_ma_power_offset")

        self.torque_range_min.label = session.get("lang.setting.4_20_ma_torque_min")
        self.torque_range_max.label = session.get("lang.setting.4_20_ma_torque_max")
        self.torque_range_offset.label = session.get("lang.setting.4_20_ma_torque_offset")

        self.thrust_range_min.label = session.get("lang.setting.4_20_ma_thrust_min")
        self.thrust_range_max.label = session.get("lang.setting.4_20_ma_thrust_max")
        self.thrust_range_offset.label = session.get("lang.setting.4_20_ma_thrust_offset")

        self.speed_range_min.label = session.get("lang.setting.4_20_ma_speed_min")
        self.speed_range_max.label = session.get("lang.setting.4_20_ma_speed_max")
        self.speed_range_offset.label = session.get("lang.setting.4_20_ma_speed_offset")

        self.output_conf.set_title(session.get("lang.setting.output_conf"))
        self.check_torque.label = session.get("lang.common.torque")
        self.check_thrust.label = session.get("lang.common.thrust")
        self.check_power.label = session.get("lang.common.power")
        self.check_speed.label = session.get("lang.common.speed")
        self.check_avg_power.label = session.get("lang.common.average_power")
        self.check_sum_power.label = session.get("lang.common.sum_power")

        self.gps_conf.set_title(session.get("lang.setting.gps_conf"))
        self.gps_ip.label = session.get("lang.setting.ip")
        self.gps_port.label = session.get("lang.setting.port")
        # self.gps_conn_check.text = session.get("lang.setting.check_gps_connection") 

        self.modbus_conf.set_title(session.get("lang.setting.modbus_conf"))
        self.modbus_ip.label = session.get("lang.setting.ip")
        self.modbus_port.label = session.get("lang.setting.port")
        # self.modbus_conn_check.text = session.get("lang.setting.check_modbus_connection")

        self.save_button.text = session.get("lang.button.save")
        self.reset_button.text = session.get("lang.button.reset")

    def before_update(self):
        self.__set_language()

    def did_mount(self):
        self.__set_language()
