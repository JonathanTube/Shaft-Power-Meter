import datetime
import flet as ft

from .custom_card import createCard


def _create_preferences():
    col = {"md": 6}
    return createCard(
        'Preference',
        ft.ResponsiveRow(controls=[
            ft.Row(
                controls=[
                    ft.Text("System Units"),
                    ft.RadioGroup(content=ft.Row([
                        ft.Radio(value=0, label="SI"),
                        ft.Radio(value=1, label="Metric")]))],
                col={"md": 6}),

            ft.Row(controls=[
                ft.Text("Language"),
                ft.RadioGroup(content=ft.Row([
                    ft.Radio(value=0, label="English"),
                    ft.Radio(value=1, label="中文")
                ]))],
                col={"md": 6}),
            ft.TextField(label="Data Refresh Interval", suffix_text="seconds")]),
        col={"xs": 12})


def _create_max_parameter():
    return createCard('Max Parameter', ft.Column(controls=[
        ft.TextField(suffix_text="rpm", label="Speed"),
        ft.TextField(suffix_text="kNm", label="Torque"),
        ft.TextField(suffix_text="kW", label="Power")]))


def _create_warning_parameter():
    return createCard('Warning Parameter', ft.Column(controls=[
        ft.TextField(suffix_text="rpm", label="Speed"),
        ft.TextField(suffix_text="kNm", label="Torque"),
        ft.TextField(suffix_text="kW", label="Power")]))


date_picker = ft.TextField(
    label="Date",
    col={"md": 6},
    on_click=lambda e: e.page.open(ft.DatePicker(
        first_date=datetime.datetime(
            year=2023, month=10, day=1),
        last_date=datetime.datetime(
            year=2024, month=10, day=1),
        on_change=handle_date_change
    )))


def handle_date_change(e):
    print(e.control.value.strftime('%Y-%m-%d'))
    date_picker.value = e.control.value.strftime('%Y-%m-%d')
    date_picker.update()


def handle_time_change(e):
    time_picker.value = e.control.value.strftime('%H:%M:%S')
    time_picker.update()


time_picker = ft.TextField(
    label="Time",
    col={"md": 6},
    on_click=lambda e: e.page.open(ft.TimePicker(
        confirm_text="Confirm",
        error_invalid_text="Time out of range",
        help_text="Pick your time slot",
        on_change=handle_time_change
    )))


def _create_utc_date_time():
    return createCard(
        'Date And Time',
        ft.ResponsiveRow(controls=[
            date_picker,
            time_picker,
            ft.Dropdown(label="Time Format", col={"md": 6},
                        options=[ft.DropdownOption(key="YYYY-MM-dd HH:mm:ss"),
                                 ft.DropdownOption(key="YYYY/MM/dd HH:mm:ss"),
                                 ft.DropdownOption(key="dd/MM/YYYY HH:mm:ss"),
                                 ft.DropdownOption(key="MM/dd/YYYY HH:mm:ss")]),
            ft.Switch(label='Sync With GPS', col={"md": 6}, value=False)]),
        col={"xs": 12})


def createGeneral():
    return ft.Column(
        expand=True,
        controls=[
            ft.ResponsiveRow(controls=[
                _create_preferences(),
                _create_max_parameter(),
                _create_warning_parameter(),
                _create_utc_date_time(),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.ElevatedButton(
                            text="Save", width=120, height=40),
                        ft.OutlinedButton(
                            text="Cancel", width=120, height=40)
                    ])
            ])
        ])


# def main(page: ft.Page):
#     page.add(createGeneral())


# ft.app(main)
