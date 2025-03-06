import flet as ft


def main(page: ft.Page):
    width = 40
    height = 40
    c1 = ft.Container(width=width, height=height,
                      bgcolor=ft.Colors.RED, content=ft.Text("c1"))
    c2 = ft.Container(width=width, height=height,
                      bgcolor=ft.Colors.GREEN, content=ft.Text("c2"))
    c3 = ft.Container(width=width, height=height,
                      bgcolor=ft.Colors.BLUE, content=ft.Text("c3"))
    c4 = ft.Container(width=width, height=height,
                      bgcolor=ft.Colors.YELLOW, content=ft.Text("c4"))

    # page.add(ft.Row(controls=[c1, c2, c3, c4]))

    # page.add(ft.Row(controls=[c1, c2, c3, c4],
    #          alignment=ft.MainAxisAlignment.CENTER))

    # page.add(ft.Row(controls=[c1, c2, c3, c4],
    #          alignment=ft.MainAxisAlignment.END))

    # page.add(ft.Column(controls=[c1, c2, c3, c4]))

    # 行布局，水平居中，垂直居中
    page.add(ft.Container(
        bgcolor=ft.Colors.AMBER_400,
        content=ft.Row(
            width=300,
            height=300,
            expand=True,
            controls=[c1, c2, c3, c4],
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
    ))

    # 列布局，水平居中，垂直居中
    # page.add(ft.Container(
    #     bgcolor=ft.Colors.AMBER_400,
    #     content=ft.Column(
    #         width=300,
    #         height=300,
    #         expand=True,
    #         controls=[c1, c2, c3, c4],
    #         alignment=ft.MainAxisAlignment.CENTER,
    #         horizontal_alignment=ft.CrossAxisAlignment.CENTER
    #     )
    # ))


ft.app(main)
