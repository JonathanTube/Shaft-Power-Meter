import datetime
import flet as ft


def _field_label(text: str):
    return ft.Text(text, weight=ft.FontWeight.W_400, width=160, text_align=ft.TextAlign.RIGHT)


def _field_container(content):
    return ft.Container(width=250, content=content, bgcolor=ft.Colors.PINK_100)


def _create_preferences():
    system_units = ft.Row(
        controls=[
            _field_label('System Units:'),
            _field_container(
                ft.RadioGroup(content=ft.Row([
                    ft.Radio(value=0, label="SI"),
                    ft.Radio(value=1, label="Metric")
                ]))
            )
        ])

    Language = ft.Row(
        controls=[
            _field_label('Language:'),
            _field_container(
                ft.RadioGroup(content=ft.Row([
                    ft.Radio(value=0, label="English"),
                    ft.Radio(value=1, label="中文")
                ]))
            )
        ])

    data_refresh_interval = ft.Row(
        controls=[
            _field_label("Data Refresh Interval:"),
            _field_container(ft.TextField(suffix="seconds"))])

    column = ft.Column(controls=[
        system_units,
        Language,
        data_refresh_interval
    ])

    return ft.Card(
        expand=True,
        content=ft.Container(
            padding=ft.padding.symmetric(30, 20),
            content=column
        )
    )


def _create_display_conf():
    speed_warning = ft.Row(
        controls=[
            _field_label("Speed Warning:"),
            _field_container(ft.TextField(suffix="rpm"))])
    speed_limit = ft.Row(
        controls=[
            _field_label("Speed Limit:"),
            _field_container(ft.TextField(suffix="rpm"))])

    torque_warning = ft.Row(
        controls=[
            _field_label("Torque Warning:"),
            _field_container(ft.TextField(suffix="kNm"))])

    torque_limit = ft.Row(
        controls=[
            _field_label("Torque Limit:"),
            _field_container(ft.TextField(suffix="kNm"))])

    power_warning = ft.Row(
        controls=[
            _field_label("Power Warning:"),
            _field_container(ft.TextField(suffix="kW"))])

    power_limit = ft.Row(
        controls=[
            _field_label("Power Limit:"),
            _field_container(ft.TextField(suffix="kW"))])

    column = ft.Column(controls=[
        ft.Row(spacing=20, controls=[speed_warning, speed_limit]),
        ft.Row(spacing=20, controls=[torque_warning, torque_limit]),
        ft.Row(spacing=20, controls=[power_warning, power_limit])
    ])

    return ft.Card(
        expand=True,
        content=ft.Container(
            padding=ft.padding.symmetric(30, 20),
            content=column
        )
    )


def _create_utc_date_time():

    def handle_change(e):
        e.page.add(
            ft.Text(f"Date changed: {e.control.value.strftime('%Y-%m-%d')}"))

    def handle_dismissal(e):
        e.page.add(ft.Text(f"DatePicker dismissed"))

    date_picker = ft.Row(
        controls=[
            _field_label('Date:'),
            ft.ElevatedButton(
                "Pick date",
                icon=ft.Icons.CALENDAR_MONTH,
                on_click=lambda e: e.page.open(
                    ft.DatePicker(
                        first_date=datetime.datetime(
                            year=2023, month=10, day=1),
                        last_date=datetime.datetime(
                            year=2024, month=10, day=1),
                        on_change=handle_change,
                        on_dismiss=handle_dismissal,
                    )))])

    time_picker = ft.Row(controls=[
        _field_label('Time:'),
        ft.ElevatedButton(
            "Pick time",
            icon=ft.Icons.TIME_TO_LEAVE,
            on_click=lambda e: e.page.open(ft.TimePicker(
                confirm_text="Confirm",
                error_invalid_text="Time out of range",
                help_text="Pick your time slot",
                on_change=handle_change,
                on_dismiss=handle_dismissal
            ))
        )
    ])

    time_format = ft.Row(
        controls=[
            _field_label("Time Format:"),
            _field_container(
                ft.Dropdown(
                    options=[
                        ft.DropdownOption(key="YYYY-MM-dd HH:mm:ss"),
                        ft.DropdownOption(key="YYYY/MM/dd HH:mm:ss"),
                        ft.DropdownOption(key="dd/MM/YYYY HH:mm:ss"),
                        ft.DropdownOption(key="MM/dd/YYYY HH:mm:ss")
                    ],
                ))])

    sync_with_gas = ft.Row(
        controls=[
            _field_label('Sync With GPS:'),
            _field_container(ft.Switch(label='Enable', value=False))
        ])

    column = ft.Column(controls=[
        date_picker,
        time_picker,
        time_format,
        sync_with_gas
    ])

    return ft.Card(
        expand=True,
        content=ft.Container(
            padding=ft.padding.symmetric(30, 20),
            content=column
        )
    )


def createGeneral():
    return ft.Column(
        expand=True,
        controls=[
            _create_preferences(),
            _create_display_conf(),
            _create_utc_date_time()
        ]
    )
