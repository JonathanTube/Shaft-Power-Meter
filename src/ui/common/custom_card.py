import flet as ft


def create_card(heading: str, body: ft.Control, col=None, expand: bool = False, height: int = None):
    if col is None:
        col = {"md": 6}
    return ft.Card(
        col=col,
        expand=expand,
        height=height,
        content=ft.Container(
            padding=ft.padding.symmetric(10, 10),
            # expand=True,
            content=ft.Column(
                expand=False,
                spacing=0,
                controls=[
                    ft.Container(
                        # expand=True,
                        padding=ft.padding.only(bottom=10),
                        content=ft.Row(
                            # expand=True,
                            controls=[
                                ft.Icon(name=ft.Icons.CYCLONE),
                                ft.Text(
                                    heading, weight=ft.FontWeight.BOLD, size=16)
                            ]
                        )),
                    ft.Container(
                        expand=expand,
                        # bgcolor=ft.Colors.RED,
                        padding=ft.padding.symmetric(0, 20),
                        content=body
                    )
                ])))
