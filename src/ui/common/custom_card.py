import flet as ft


def create_card(heading: str, body: ft.Control, col=None, expand: bool = False, height: int = None):
    if col is None:
        col = {"md": 6}

    return ft.Card(
        col=col,
        expand=expand,
        height=height,
        content=ft.Container(
            # bgcolor="pink",
            padding=ft.padding.symmetric(10, 10),
            expand=expand,
            content=ft.Column(
                expand=expand,
                spacing=0,
                controls=[
                    ft.Container(
                        expand=False,
                        padding=ft.padding.only(bottom=10),
                        content=ft.Row(
                            expand=False,
                            controls=[
                                ft.Icon(name=ft.Icons.CYCLONE),
                                ft.Text(
                                    heading, weight=ft.FontWeight.BOLD, size=16)
                            ]
                        )),
                    ft.Container(
                        expand=False,
                        # bgcolor=ft.Colors.BLUE,
                        padding=ft.padding.symmetric(0, 20),
                        content=body
                    )
                ])))
