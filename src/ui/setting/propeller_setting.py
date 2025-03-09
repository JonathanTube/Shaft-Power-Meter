import flet as ft
from src.ui.common.custom_card import create_card


def _createMCROperatingPoint():
    col = {"md": 6}
    return create_card(
        'MCR Operating Point',
        ft.ResponsiveRow(
            controls=[
                ft.TextField(label="RPM", suffix_text='[1/min]', col=col),
                ft.TextField(label="Shaft Power", suffix_text='[kW]', col=col)
            ]),
        col={"xs": 12}
    )


def _createNormalPropellerCurve():
    return create_card('Normal Propeller Curve (1)', ft.Column(controls=[
        ft.TextField(label="RPM Left", suffix_text='[%]'),
        ft.TextField(label="BHP Left", suffix_text='[%]'),
        ft.TextField(label="RPM Right", suffix_text='[%]'),
        ft.TextField(label="BHP Right", suffix_text='[%]'),
        ft.TextField(label="Line Color")
    ]))


def _createLightPropellerCurve():
    return create_card('Light Propeller Curve (2)', ft.Column(controls=[
        ft.TextField(label="Light", suffix_text="[% below (1)]"),
        ft.TextField(label="Line Color")
    ]))


def _createSpeedLimitCruve():
    return create_card('Speed Limit Curve (3)', ft.Column(controls=[
        ft.TextField(label="Limit", suffix_text="[% MCR rpm]"),
        ft.TextField(label="Line Color")
    ]))


def _createTorqueLoadLimitCurve():
    return create_card('Torque/Load Limit Curve (4)', ft.Column(controls=[
        ft.TextField(label="RPM Left", suffix_text='[%]'),
        ft.TextField(label="BHP Left", suffix_text='[%]'),
        ft.TextField(label="RPM Right", suffix_text='[%]'),
        ft.TextField(label="BHP Right", suffix_text='[%]'),
        ft.TextField(label="Line Color")
    ]))


def _createOverloadCurve():
    col = {"md": 6}
    return create_card('Overload Curve (5)',
                      ft.ResponsiveRow(controls=[
                          ft.TextField(label="Overload",
                                       suffix_text="[% above (4)]", col=col),
                          ft.TextField(label="Line Color", col=col),
                          ft.Switch(label="Overload Alarm",
                                    label_position=ft.LabelPosition.LEFT, col=col)
                      ]),
                      col={"xs": 12})


def createPropellerSetting():
    return ft.Column(
        expand=True,
        # scroll=ft.ScrollMode.AUTO, 这里有bug，如果添加了，外部页面就会居中
        controls=[
            ft.ResponsiveRow(
                expand=True,
                controls=[
                    _createMCROperatingPoint(),
                    _createNormalPropellerCurve(),
                    _createTorqueLoadLimitCurve(),
                    _createLightPropellerCurve(),
                    _createSpeedLimitCruve(),
                    _createOverloadCurve(),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.ElevatedButton(
                                text="Save", width=120, height=40),
                            ft.OutlinedButton(
                                text="Cancel", width=120, height=40)
                        ])
                ])])


# def main(page: ft.Page):
#     page.add(createPropellerSetting())


# ft.app(main)
