import flet as ft
from dateutil.relativedelta import relativedelta
from common.operation_type import OperationType
from db.models.date_time_conf import DateTimeConf
from db.models.operation_log import OperationLog
from db.models.user import User
from db.models.zero_cal_info import ZeroCalInfo
from db.models.zero_cal_record import ZeroCalRecord
from ui.common.permission_check import PermissionCheck
from ui.common.toast import Toast
from common.global_data import gdata


class ZeroCalExecutor(ft.Container):
    def __init__(self):
        super().__init__()
        self.__load_data()

    def __load_data(self):
        # 查询最近一次[接受]的调零记录
        self.latest_accepted_zero_cal: ZeroCalInfo = ZeroCalInfo.select().where(ZeroCalInfo.state == 1).order_by(ZeroCalInfo.id.desc()).first()
        # 查询最新的一条进行中的记录
        self.latest_zero_cal: ZeroCalInfo = ZeroCalInfo.select().where(ZeroCalInfo.state == 0).order_by(ZeroCalInfo.id.desc()).first()

        date_time_conf: DateTimeConf = DateTimeConf.get()
        self.date_format = date_time_conf.date_format

    def __get_next_performing_time(self):
        zero_cal_last_performed = "None"
        recommend_next_performing_time = "None"

        if self.latest_accepted_zero_cal is not None:
            format_str = f'{self.date_format} %H:%M'
            zero_cal_last_performed = self.latest_accepted_zero_cal.utc_date_time.strftime(format_str)
            # 默认每隔6个月建议调零一次
            recommend_next_performing_time = (self.latest_accepted_zero_cal.utc_date_time + relativedelta(months=+6)).strftime(format_str)

        return zero_cal_last_performed, recommend_next_performing_time

    def __create_tips_card(self):
        self.state_info = ft.Text(self.page.session.get("lang.zero_cal.on_progress"), color=ft.Colors.GREEN_600, visible=self.latest_zero_cal is not None and self.latest_zero_cal.state == 0)

        zero_cal_last_performed, recommend_next_performing_time = self.__get_next_performing_time()

        self.zero_cal_last_performed = ft.Text(zero_cal_last_performed)

        self.recommend_next_performing_time = ft.Text(recommend_next_performing_time)

        row = ft.Row(
            height=40,
            spacing=20,
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(self.page.session.get("lang.zero_cal.last_performed")),
                        self.zero_cal_last_performed
                    ]),
                ft.Row(
                    controls=[
                        ft.Text(self.page.session.get("lang.zero_cal.recommend_next_performing_time")),
                        self.recommend_next_performing_time
                    ]),
                self.state_info
            ]
        )

        self.tips_card = ft.Card(content=ft.Container(
            padding=ft.padding.symmetric(0,10),
            content=row
        ))

    def __create_current_offset(self):
        self.current_torque_offset = ft.Text(round(gdata.torque_offset,10))
        self.current_thrust_offset = ft.Text(round(gdata.thrust_offset,10))
        row = ft.Row(
            height=40,
            spacing=20,
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(f'{self.page.session.get("lang.zero_cal.mv_per_v_for_torque")}:'),
                        self.current_torque_offset
                    ]),
                ft.Row(
                    controls=[
                        ft.Text(f'{self.page.session.get("lang.zero_cal.mv_per_v_for_thrust")}:'),
                        self.current_thrust_offset
                    ])
            ]
        )

        self.current_offset = ft.Card(content=ft.Container(
            padding=ft.padding.symmetric(0,10),
            content=row
        ))

    def __get_table_rows(self):
        rows = []
        if self.latest_zero_cal is not None and self.latest_zero_cal.state == 0:
            records: dict[ZeroCalRecord] = self.latest_zero_cal.records
            for index, record in enumerate(records):
                rows.append(ft.DataRow(cells=[
                    ft.DataCell(ft.Text(f'#{index + 1}')),
                    ft.DataCell(ft.Text(round(record.mv_per_v_for_torque,10))),
                    ft.DataCell(ft.Text(round(record.mv_per_v_for_thrust,10)))
                ]))
        return rows

    def __get_new_avg(self):
        avg_torque = 0
        avg_thrust = 0

        if self.latest_zero_cal is None:
            return [avg_torque, avg_thrust]

        if len(self.latest_zero_cal.records) == 0:
            return [avg_torque, avg_thrust]

        sum_torque = 0
        sum_thrust = 0
        records: dict[ZeroCalRecord] = self.latest_zero_cal.records[:8]
        for record in records:
            sum_torque += record.mv_per_v_for_torque
            sum_thrust += record.mv_per_v_for_thrust

        avg_torque = (sum_torque / len(records)) * -1
        avg_thrust = (sum_thrust / len(records)) * -1

        return [avg_torque, avg_thrust]

    def __create_instant_records(self):
        table_rows = self.__get_table_rows()
        [avg_torque, avg_thrust] = self.__get_new_avg()

        self.table = ft.DataTable(
            col={"xs": 12},
            width=920,
            height=320,
            heading_row_height=40,
            data_row_min_height=35,
            data_row_max_height=35,
            expand=True,
            columns=[
                ft.DataColumn(ft.Text("No.", size=14, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text(self.page.session.get("lang.zero_cal.mv_per_v_for_torque"), size=14, weight=ft.FontWeight.W_500)),
                ft.DataColumn(ft.Text(self.page.session.get("lang.zero_cal.mv_per_v_for_thrust"), size=14, weight=ft.FontWeight.W_500))
            ],
            rows=table_rows)

        self.new_avg_torque = ft.Text(round(avg_torque,10))
        self.new_avg_thrust = ft.Text(round(avg_thrust,10))

        self.table_card = ft.Card(content=self.table)

        self.result_card = ft.Card(
            visible=self.latest_zero_cal is not None,
            content=ft.Container(
                    padding=ft.padding.symmetric(0,10),
                    content=ft.Row(
                        height=40,
                        expand=True,
                        controls=[
                            ft.Text(self.page.session.get("lang.zero_cal.new_torque_offset")), self.new_avg_torque,
                            ft.Text(self.page.session.get("lang.zero_cal.new_thrust_offset")), self.new_avg_thrust
                        ]
                    )
            )
        )

        self.instant_records = ft.Column(
            expand=True,
            spacing=0,
            controls=[
                self.table_card,
                self.result_card
            ]
        )

    def __on_start_permission(self, e):
        self.page.open(PermissionCheck(self.__on_start, 0))
        
    def __on_start(self, user: User):
        ZeroCalInfo.create(utc_date_time=gdata.utc_date_time, state=0)
        self.__load_data()
        # 控制Tips过程label显示
        self.state_info.visible = True
        self.state_info.update()
        # 控制按钮显示
        self.start_button.visible = False
        self.start_button.update()

        self.accept_button.visible = len(self.latest_zero_cal.records) == 8
        self.accept_button.update()

        self.abort_button.visible = True
        self.abort_button.update()

        self.fetch_button.visible = len(self.latest_zero_cal.records) < 8
        self.fetch_button.update()

        OperationLog.create(
            user_id=user.id,
            utc_date_time=gdata.utc_date_time,
            operation_type=OperationType.ZERO_CAL,
            operation_content=""
        )
        
        Toast.show_success(self.page, message=self.page.session.get("lang.zero_cal.started"))

    def __reset_to_start(self):
        self.__load_data()
        self.state_info.visible = False
        self.state_info.update()

        zero_cal_last_performed, recommend_next_performing_time = self.__get_next_performing_time()

        self.zero_cal_last_performed.value = zero_cal_last_performed
        self.zero_cal_last_performed.update()
        self.recommend_next_performing_time.value = recommend_next_performing_time
        self.recommend_next_performing_time.update()

        self.table.rows = []
        self.table.update()

        self.accept_button.visible = False
        self.accept_button.update()

        self.abort_button.visible = False
        self.abort_button.update()

        self.start_button.visible = True
        self.start_button.update()

        self.fetch_button.visible = False
        self.fetch_button.update()

    def __on_accept(self, e):
        # if times of recording is less than 8, do nothing.
        if len(self.latest_zero_cal.records) < 8:
            return

        # 设置为已接受
        query = ZeroCalInfo.update(state=1).where(ZeroCalInfo.id == self.latest_zero_cal.id)
        query.execute()

        self.__reset_to_start()

        gdata.torque_offset = self.latest_accepted_zero_cal.torque_offset
        gdata.thrust_offset = self.latest_accepted_zero_cal.thrust_offset
        self.current_torque_offset.value = round(gdata.torque_offset,10)
        self.current_thrust_offset.value = round(gdata.thrust_offset,10)
        self.current_offset.update()

        Toast.show_success(e.page, message=self.page.session.get("lang.zero_cal.accepted"))

    def __on_abort(self, e):
        query = ZeroCalInfo.update(state=2).where(ZeroCalInfo.id == self.latest_zero_cal.id)
        query.execute()

        self.__reset_to_start()
        Toast.show_success(e.page, message=self.page.session.get("lang.zero_cal.aborted"))

    def __on_fetch(self, e):
        # 如果主记录为空，说明还没开始，跳过
        if self.latest_zero_cal is None:
            return

        if len(self.latest_zero_cal.records) >= 8:
            return

        ZeroCalRecord.create(
            zero_cal_info=self.latest_zero_cal.id,
            mv_per_v_for_torque=gdata.sps1_mv_per_v_for_torque,
            mv_per_v_for_thrust=gdata.sps1_mv_per_v_for_thrust
        )

        self.result_card.visible = True
        self.result_card.update()

        self.__load_data()

        self.accept_button.visible = len(self.latest_zero_cal.records) == 8
        self.accept_button.update()

        self.fetch_button.visible = len(self.latest_zero_cal.records) < 8
        self.fetch_button.update()

        # 刷新表格与统计
        self.table.rows = self.__get_table_rows()
        self.table.update()

        # 获得计算结果
        [avg_torque, avg_thrust] = self.__get_new_avg()

        # 保存值到数据库
        query = (ZeroCalInfo.update(
            torque_offset=avg_torque,
            thrust_offset=avg_thrust
        ).where(ZeroCalInfo.id == self.latest_zero_cal.id))
        query.execute()

        # 筛选平均值
        self.new_avg_torque.value = round(avg_torque,10)
        self.new_avg_torque.update()

        self.new_avg_thrust.value = round(avg_thrust,10)
        self.new_avg_thrust.update()

        Toast.show_success(e.page)

    def build(self):
        self.start_button = ft.FilledButton(text=self.page.session.get("lang.zero_cal.start"), bgcolor=ft.Colors.GREEN_900, color=ft.Colors.WHITE, width=120, height=40, on_click=self.__on_start_permission)
        self.accept_button = ft.FilledButton(text=self.page.session.get("lang.zero_cal.accept"), bgcolor=ft.Colors.LIGHT_GREEN, color=ft.Colors.WHITE, width=120, height=40, on_click=self.__on_accept)
        self.fetch_button = ft.FilledButton(text=self.page.session.get("lang.zero_cal.fetch_data"), bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE, width=120, height=40, on_click=self.__on_fetch)
        self.abort_button = ft.FilledButton(text=self.page.session.get("lang.zero_cal.abort"), bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, width=120, height=40, on_click=self.__on_abort)

        self.__create_tips_card()
        self.__create_current_offset()
        self.__create_instant_records()

        if self.latest_zero_cal is None:
            self.start_button.visible = True
            self.accept_button.visible = False
            self.abort_button.visible = False
            self.fetch_button.visible = False

        elif self.latest_zero_cal.state == 0:  # 调零中
            self.start_button.visible = False
            self.accept_button.visible = len(self.latest_zero_cal.records) == 8
            self.abort_button.visible = True
            self.fetch_button.visible = len(self.latest_zero_cal.records) < 8

        elif self.latest_zero_cal.state in (1, 2):  # 已接受 # 已废弃
            self.start_button.visible = True
            self.accept_button.visible = False
            self.abort_button.visible = False
            self.fetch_button.visible = False

        self.content = ft.Column(
            spacing=0,
            controls=[
                self.tips_card,
                self.current_offset,
                self.instant_records,
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        self.start_button,
                        self.accept_button,
                        self.fetch_button,
                        self.abort_button
                    ])
            ])
