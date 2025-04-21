import flet as ft


def main(page: ft.Page):
    def on_pan_update(e: ft.DragUpdateEvent):
        e.control.top = max(0, e.control.top + e.delta_y)
        e.control.left = max(0, e.control.left + e.delta_x)
        e.control.update()

    gd = ft.GestureDetector(
        top=0,
        left=0,
        mouse_cursor=ft.MouseCursor.MOVE,
        drag_interval=10,
        on_pan_update=on_pan_update,
        content=ft.Container(bgcolor=ft.Colors.BLUE, width=50, height=50)
    )

    page.add(ft.Stack([gd]))


ft.app(main)
