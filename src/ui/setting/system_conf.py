import flet as ft

from .custom_card import createCard


def _create_settings_card():
    return createCard('Settings', ft.Column(
        controls=[
            ft.Row(controls=[
                ft.Text("Running Mode"),
                ft.RadioGroup(content=ft.Row([
                    ft.Radio(value=0, label="Master"),
                    ft.Radio(value=1, label="Slave")
                ]))
            ]),

            ft.TextField(label="Master IP"),
            ft.TextField(label="Master Port"),
            ft.Switch(label="Display Thrust",
                      label_position=ft.LabelPosition.LEFT),
            ft.Row(controls=[
                ft.Text("Amount Of Propeller"),
                ft.RadioGroup(content=ft.Row([
                   ft.Radio(value=0, label="Single"),
                   ft.Radio(value=1, label="Dual")
                   ]))
            ]),

            ft.Switch(label="ShaPoLi",
                      label_position=ft.LabelPosition.LEFT)])
    )


def _create_ship_info():
    return createCard('Ship Info', ft.Column(
        controls=[
            ft.TextField(label="Ship Type"),
            ft.TextField(label="Ship Name"),
            ft.TextField(label="IMO Number"),
            ft.TextField(label="Ship Size")
        ]
    ))


def _create_factor_conf():
    return createCard('Factor Conf.', ft.Column(
        controls=[
            ft.TextField(label="Shaft Outer Diameter(D)", suffix_text="mm"),
            ft.TextField(label="Shaft Inner Diameter(d)", suffix_text="mm"),
            ft.TextField(label="Sensitivity Factor(k)"),
            ft.TextField(label="Elastic Modulus(E)", suffix_text="Gpa"),
            ft.TextField(label="Poisson's Ratio(μ)", suffix_text="Gpa")
        ]
    ))


def createSystemConf():
    return ft.ResponsiveRow(
        # expand=True,
        alignment=ft.CrossAxisAlignment.START,
        controls=[
            _create_settings_card(),
            _create_ship_info(),
            _create_factor_conf(),
            ft.Row(
                # expand=True,
                col={'xs': 12},
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.ElevatedButton(text="Save", width=120, height=40),
                    ft.OutlinedButton(text="Cancel", width=120, height=40)
                ])
        ]
    )


# def main(page: ft.Page):
#     page.add(createSystemConf())


# ft.app(main)
