import time

import flet as ft


class Toast:
    @staticmethod
    def show_success(page: ft.Page, message: str):
        Toast.show_toast(page, message, ft.Colors.GREEN_500, ft.Colors.WHITE)

    @staticmethod
    def show_warning(page: ft.Page, message: str):
        Toast.show_toast(page, message, ft.Colors.ORANGE_500, ft.Colors.WHITE)

    @staticmethod
    def show_error(page: ft.Page, message: str):
        Toast.show_toast(page, message, ft.Colors.RED_500, ft.Colors.WHITE)

    @staticmethod
    def show_toast(page: ft.Page, message: str, bg_color: ft.Colors, color: ft.Colors, duration=2):
        # 创建 Toast 控件
        toast = ft.Container(
            expand=True,
            content=ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[ft.Text(message, size=16, color=color)]),
            bgcolor=bg_color,
            padding=10,
            border_radius=5,
            opacity=0,  # 初始透明
            animate_opacity=300  # 透明度动画过渡时间
        )

        # 覆盖在整个页面上方（绝对定位）
        page.overlay.append(toast)
        page.update()

        # 显示动画
        toast.opacity = 1
        page.update()

        # 定时隐藏并移除
        time.sleep(duration)
        toast.opacity = 0
        page.update()
        page.overlay.remove(toast)
        page.update()
