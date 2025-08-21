import logging
import asyncio
import flet as ft


class Toast:
    @staticmethod
    def show_success(page: ft.Page, message: str = None, duration: int = 5000):
        if page is None or page.session is None:
            return
        msg = message if message is not None else page.session.get("lang.toast.success")
        # Toast.show_toast(page, msg, ft.Colors.GREEN_500, ft.Colors.WHITE)
        page.open(
            ft.SnackBar(
                ft.Text(msg, color=ft.Colors.WHITE, expand=True, text_align=ft.TextAlign.CENTER),
                bgcolor=ft.Colors.GREEN,
                show_close_icon=True,
                duration=duration
            )
        )

    @staticmethod
    def show_warning(page: ft.Page, message: str = None, duration: int = 5000):
        if page is None or page.session is None:
            return
        msg = message if message is not None else page.session.get("lang.toast.warning")
        # Toast.show_toast(page, msg, ft.Colors.ORANGE_500, ft.Colors.WHITE)
        page.open(
            ft.SnackBar(
                ft.Text(msg, color=ft.Colors.WHITE, expand=True, text_align=ft.TextAlign.CENTER),
                bgcolor=ft.Colors.ORANGE,
                show_close_icon=True,
                duration=duration
            )
        )

    @staticmethod
    def show_error(page: ft.Page, message: str = None, duration: int = 5000):
        if page is None or page.session is None:
            return
        msg = message if message is not None else page.session.get("lang.toast.error")
        # Toast.show_toast(page, msg, ft.Colors.RED_500, ft.Colors.WHITE, auto_hide=auto_hide)
        page.open(
            ft.SnackBar(
                ft.Text(msg, color=ft.Colors.WHITE, expand=True, text_align=ft.TextAlign.CENTER),
                bgcolor=ft.Colors.RED,
                show_close_icon=True,
                duration=duration
            )
        )