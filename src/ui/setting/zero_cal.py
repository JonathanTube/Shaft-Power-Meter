import flet as ft

from ui.common.custom_card import createCard


def _create_zero_cal():
    return ft.Column(
        controls=[
            createCard(
                heading="Tips",
                body=ft.ResponsiveRow(controls=[
                    ft.Text(
                        "Zero calibration last performed：2024/01/20 13:00:01",
                        col={"md": 6}
                    ),
                    ft.Text(
                        "Recommand Next performing time：2024/07/18 13:00:01",
                        col={"md": 6}
                    )
                ])),

            ft.ResponsiveRow(controls=[
                createCard(heading="Instant Records", body=ft.DataTable(
                    col={"xs": 12},
                    expand=True,
                    columns=[
                        ft.DataColumn(ft.Text("No.")),
                        ft.DataColumn(
                            ft.Text("Torque(Nm)"), numeric=True),
                        ft.DataColumn(
                            ft.Text("Thrust(N)"), numeric=True),
                    ],
                    rows=[
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text("#1")),
                                ft.DataCell(ft.Text(11)),
                                ft.DataCell(ft.Text(22))
                            ])
                    ])),
                createCard(
                    heading="Progress",
                    body=ft.PieChart(
                        col={"md": 6},
                        sections=[
                            ft.PieChartSection(
                                40,
                                title="40%",
                                color=ft.Colors.GREEN
                            ),
                            ft.PieChartSection(
                                30,
                                title="30%",
                                color=ft.Colors.GREY_200
                            )
                        ]))
            ])
        ])


def _create_history():
    return ft.Column(
        controls=[
            createCard(heading="Search", body=ft.Row(controls=[
                ft.TextField(label="Start Date"),
                ft.TextField(label="End Date")
            ])),
            createCard(heading="History", body=ft.DataTable(
                expand=True,
                columns=[
                    ft.DataColumn(ft.Text("No.")),
                    ft.DataColumn(ft.Text("Date And Time")),
                    ft.DataColumn(
                        ft.Text("Torque Offset(Nm)"), numeric=True),
                    ft.DataColumn(
                        ft.Text("Thrust Offset(N)"), numeric=True),
                    ft.DataColumn(
                        ft.Text("Error Ratio(%)"), numeric=True),
                    ft.DataColumn(
                        ft.Text("Accepted"))
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text("#1")),
                            ft.DataCell(ft.Text(11)),
                            ft.DataCell(ft.Text(22)),
                            ft.DataCell(ft.Text(33)),
                            ft.DataCell(ft.Text(44)),
                            ft.DataCell(ft.Row(controls=[ft.Text('Yes'), ft.Icon(
                                name=ft.Icons.ASSIGNMENT_TURNED_IN_OUTLINED, size=20, color=ft.Colors.GREEN_500)]))
                        ])
                ]))
        ])


def createZeroCal():
    return ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Zero Cal.",
                icon=ft.Icons.ADJUST_OUTLINED,
                content=ft.Container(
                    padding=ft.padding.symmetric(10, 20),
                    content=_create_zero_cal()
                )
            ),

            ft.Tab(
                text="Zero Cal. History",
                icon=ft.icons.HISTORY_OUTLINED,
                content=ft.Container(
                    padding=ft.padding.symmetric(10, 20),
                    content=_create_history()
                )
            )

        ],
        expand=True
    )
