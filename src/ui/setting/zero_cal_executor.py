import random

import flet as ft
from dateutil.relativedelta import relativedelta
from datetime import datetime

from src.database.models.zero_cal_info import ZeroCalInfo
from src.database.models.zero_cal_record import ZeroCalRecord
from src.ui.common.custom_card import create_card
from src.ui.common.toast import Toast


class ZeroCalExecutor:
    def __init__(self):
        self.__load_data()

        # 初始化操作按钮
        self.start_button = ft.FilledButton(text="Start", width=120, height=40, on_click=self.__on_start)
        self.accept_button = ft.FilledButton(text="Accept", bgcolor=ft.Colors.GREEN, width=120, height=40,
                                on_click=self.__on_accept)
        self.abort_button = ft.FilledButton(text="Abort", bgcolor=ft.Colors.RED, width=120, height=40,
                                on_click=self.__on_abort)

        self.__create_tips_card()
        self.__create_instant_records()
        self.__create_progress_card()


    def __load_data(self):
        # 查询最近一次[接受]的调零记录
        self.latest_accepted_zero_cal = ZeroCalInfo.select().where(ZeroCalInfo.state == 1).order_by(
            ZeroCalInfo.id.desc()).first()
        # 查询最新的一条记录
        self.latest_zero_cal = ZeroCalInfo.select().order_by(ZeroCalInfo.id.desc()).first()

    def __create_tips_card(self):
        if self.latest_accepted_zero_cal is None:
            zero_cal_last_performed = 'None'
            recommend_next_performing_time = 'None'
        else:
            zero_cal_last_performed = self.latest_accepted_zero_cal.utc_date_time
            # 默认每隔6个月建议调零一次
            recommend_next_performing_time = zero_cal_last_performed + relativedelta(months=+6)

        self.state_info = ft.Text('Zero Cal. is on progress.',
                                  color=ft.Colors.GREEN_600,
                                  size=20, col={"md": 12},
                                  visible=self.latest_zero_cal is not None and self.latest_zero_cal.state == 0)

        self.tips_card = create_card(
            heading="Tips",
            body=ft.ResponsiveRow(
                controls=[
                    self.state_info,

                    ft.Text(f"Zero calibration last performed：{zero_cal_last_performed}",
                            size=16, col={"md": 6}),

                    ft.Text(f"Recommend next performing time：{recommend_next_performing_time}",
                            size=16, col={"md": 6})
                ]
            )
        )

    def __get_table_rows(self):
        rows = []
        if self.latest_zero_cal is not None and self.latest_zero_cal.state == 0:
            for index, record in enumerate(self.latest_zero_cal.records):
                rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f'#{index + 1}')),
                    ft.DataCell(ft.Text(record.torque)),
                    ft.DataCell(ft.Text(record.thrust))
                ]))
        return rows

    def __get_new_avg(self):
        avg_torque = 0
        avg_thrust = 0

        if self.latest_zero_cal is not None and self.latest_zero_cal.state == 0:
            sum_torque = 0
            sum_thrust = 0
            records = self.latest_zero_cal.records[:8]
            for record in records:
                sum_torque += record.torque
                sum_thrust += record.thrust

            avg_torque = round(sum_torque / len(records), 2)
            avg_thrust = round(sum_thrust / len(records), 2)

        return [avg_torque, avg_thrust]


    def __get_error_ratio(self):
        error_ratio_torque = 0
        error_ratio_thrust = 0

        if self.latest_zero_cal is None:
            return [error_ratio_torque, error_ratio_thrust]
        if self.latest_zero_cal.state != 0:
            return [error_ratio_torque, error_ratio_thrust]
        if len(self.latest_zero_cal.records) < 9:
            return [error_ratio_torque, error_ratio_thrust]

        record_1st = self.latest_zero_cal.records[0]
        record_9th = self.latest_zero_cal.records[8]

        error_ratio_torque = round(abs(record_9th.torque - record_1st.torque) / record_1st.torque * 100,2)
        error_ratio_thrust = round(abs(record_9th.thrust - record_1st.thrust) / record_1st.thrust * 100)

        return [error_ratio_torque, error_ratio_thrust]


    def __create_instant_records(self):
        table_rows = self.__get_table_rows()
        [avg_torque, avg_thrust] = self.__get_new_avg()
        [error_ratio_torque, error_ratio_thrust] = self.__get_error_ratio()

        self.table = ft.DataTable(
                col={"xs": 12},
                heading_row_height=35,
                data_row_min_height=30,
                data_row_max_height=30,
                expand=True,
                columns=[
                    ft.DataColumn(ft.Text("No.")),
                    ft.DataColumn(ft.Text("Torque value"), numeric=True),
                    ft.DataColumn(ft.Text("Thrust value"), numeric=True)
                ],
                rows=table_rows)

        self.new_avg_torque = ft.Text(avg_torque)
        self.new_avg_thrust = ft.Text(avg_thrust)
        self.error_ratio_torque = ft.Text(f"{error_ratio_torque}%")
        self.error_ratio_thrust = ft.Text(f"{error_ratio_thrust}%")

        self.instant_records = create_card(
            heading="Instant Records",
            height=440,
            body=ft.Column(
                expand=True,
                controls=[
                    self.table,
                    ft.Row(
                        expand=True,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(controls=[ft.Text("New Torque Avg:"), self.new_avg_torque]),
                            ft.Row(controls=[ft.Text("New Thrust Avg:"), self.new_avg_thrust])
                        ]),
                    ft.Row(
                        expand=True,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Row(controls=[ft.Text("Torque Error Ratio:"), self.error_ratio_torque]),
                            ft.Row(controls=[ft.Text("Thrust Error Ratio:"), self.error_ratio_thrust])
                        ])
                ]))


    def __create_progress_card(self):
        green_val = len(self.latest_zero_cal.records) * 10
        self.pie_chart_green = ft.PieChartSection(green_val, color=ft.Colors.GREEN)
        self.pie_chart_gray = ft.PieChartSection(90 - green_val,color=ft.Colors.GREY_200)
        self.pie_chart = ft.PieChart(col={"md": 6}, sections=[self.pie_chart_green,self.pie_chart_gray])
        self.progress_card = create_card(
            heading="Progress",
            height=440,
            body= self.pie_chart
        )

    def __on_start(self, e):
        ZeroCalInfo.create(utc_date_time=datetime.now(), state=0)
        Toast.show_success(e.page, message="zero cal. started")
        # 控制Tips过程label显示
        self.state_info.visible = True
        self.state_info.update()
        # 控制按钮显示
        self.start_button.visible = False
        self.start_button.update()

        self.accept_button.visible = True
        self.accept_button.update()

        self.abort_button.visible = True
        self.abort_button.update()

    def __on_accept(self, e):
        pass

    def __on_abort(self, e):
        self.latest_zero_cal.update(state=2)
        Toast.show_success(e.page, message="zero cal. aborted")
        # 控制Tips过程label显示
        self.state_info.visible = False
        self.state_info.update()
        # 控制按钮显示
        self.start_button.visible = True
        self.start_button.update()

        self.accept_button.visible = False
        self.accept_button.update()

        self.abort_button.visible = False
        self.abort_button.update()
        # 清空表格
        self.table.rows = []

    def __on_stimulate(self,e):
        if len(self.latest_zero_cal.records) >= 9:
            return

        ZeroCalRecord.create(
            zero_cal_info=self.latest_zero_cal.id,
            torque=random.randint(100,200),
            thrust=random.randint(100,200)
        )
        self.latest_zero_cal = ZeroCalInfo.select().order_by(ZeroCalInfo.id.desc()).first()
        # 刷新表格与统计
        self.table.rows = self.__get_table_rows()
        self.table.update()

        # 筛选平均值
        [avg_torque, avg_thrust] = self.__get_new_avg()

        self.new_avg_torque.value = avg_torque
        self.new_avg_torque.update()

        self.new_avg_thrust.value = avg_thrust
        self.new_avg_thrust.update()

        # 刷新误差值
        [error_ratio_torque, error_ratio_thrust] = self.__get_error_ratio()

        self.error_ratio_torque.value = f"{error_ratio_torque}%"
        self.error_ratio_torque.update()

        self.error_ratio_thrust.value = f"{error_ratio_thrust}%"
        self.error_ratio_thrust.update()

        # 刷新进度环
        self.pie_chart_green.value += 10
        self.pie_chart_gray.update()
        self.pie_chart_gray.value -= 10
        self.pie_chart_gray.update()

        Toast.show_success(e.page, message="fake data has been recorded")

    def create(self):
        if self.latest_zero_cal is None:
            self.start_button.visible = True
            self.accept_button.visible = False
            self.abort_button.visible = False

        elif self.latest_zero_cal.state == 0:  # 调零中
            self.start_button.visible = False
            self.accept_button.visible = True
            self.abort_button.visible = True

        elif self.latest_zero_cal.state in (1, 2):  # 已接受 # 已废弃
            self.start_button.visible = True
            self.accept_button.visible = False
            self.abort_button.visible = False

        # 模拟造数据按钮
        stimulate_button = ft.FilledButton(text="Stimulate Data", color=ft.Colors.ORANGE,
                                                width=120, height=40, on_click=self.__on_stimulate)

        return ft.Column(
            controls=[
                self.tips_card,
                ft.ResponsiveRow(controls=[
                    self.instant_records,
                    self.progress_card
                ]),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        self.start_button,
                        self.accept_button,
                        self.abort_button,
                        stimulate_button
                    ])
            ])
