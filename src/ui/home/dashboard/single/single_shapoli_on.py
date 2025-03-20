import flet as ft

from ui.common.meter_half import MeterHalf


class SingleShaPoLiOn(ft.Container):
    def __init__(self):
        super().__init__()
        self.content = self.__create()
        self.expand = True

    def __create_left(self):
        column = ft.Column(
            expand=False,
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text('EEXI Limited Power(%)',
                        weight=ft.FontWeight.BOLD, size=20),
                MeterHalf(radius=180)
            ])

        container = ft.Container(
            expand=False, padding=ft.padding.symmetric(10, 10), content=column)

        self.left = ft.Card(expand=False, content=container)

    @staticmethod
    def __create_small_card(heading: str, controls: list[ft.Control]):
        return ft.Card(
            expand=True,
            content=ft.Stack(
                controls=[
                    ft.Text(heading, weight=ft.FontWeight.W_600,
                            size=16, left=10, top=10),
                    ft.Row(controls=controls, right=10, bottom=30)
                ]
            ))

    def __create_right(self):
        self.power_text = ft.Text('9999', size=24, weight=ft.FontWeight.W_500)
        self.speed_text = ft.Text('8888', size=24, weight=ft.FontWeight.W_500)
        self.torque_text = ft.Text('7777', size=24, weight=ft.FontWeight.W_500)
        self.thrust_text = ft.Text('6666', size=24, weight=ft.FontWeight.W_500)

        content = ft.Column(
            expand=True,
            controls=[
                ft.Row(
                    expand=True,
                    controls=[
                        self.__create_small_card(
                            heading="Power",
                            controls=[self.power_text, ft.Text('kw', size=18)]
                        ),
                        self.__create_small_card(
                            heading="Speed",
                            controls=[self.speed_text, ft.Text('rpm', size=18)]
                        )
                    ]),
                ft.Row(
                    expand=True,
                    controls=[
                        self.__create_small_card(
                            heading="Torque",
                            controls=[self.torque_text,
                                      ft.Text('kNm', size=18)]
                        ),
                        self.__create_small_card(
                            heading="Thrust",
                            controls=[self.thrust_text, ft.Text('kN', size=18)]
                        )
                    ])
            ]
        )

        self.right = ft.Container(
            expand=False, width=360, height=300, content=content)

    def __create(self):
        self.__create_left()
        self.__create_right()
        # empty_placeholder = ft.Container(width=150, height=100)
        return ft.Row(
            expand=False,
            # alignment=ft.MainAxisAlignment.CENTER,
            # vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[self.left, self.right]
        )
