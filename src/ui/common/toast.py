import logging
import asyncio
import flet as ft


class Toast:
    @staticmethod
    def show_success(page: ft.Page, message: str = None, duration: int = 5):
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
    def show_warning(page: ft.Page, message: str = None, duration: int = 5):
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
    def show_error(page: ft.Page, message: str = None, duration: int = 5):
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
    # @staticmethod
    # def show_toast(
    #     page: ft.Page,
    #     message: str,
    #     bg_color: ft.Colors,
    #     color: ft.Colors,
    #     duration: float = 2,
    #     auto_hide: bool = True
    # ):
    #     try:
    #         if page and page.overlay:
    #             # 创建 Toast 控件
    #             toast = ft.Container(
    #                 expand=True,
    #                 content=ft.Row(
    #                     expand=False,
    #                     alignment=ft.MainAxisAlignment.CENTER,
    #                     controls=[ft.Text(message, size=16, color=color)]
    #                 ),
    #                 bgcolor=bg_color,
    #                 padding=10,
    #                 border_radius=5,
    #                 opacity=0,  # 初始透明
    #                 animate_opacity=300  # 透明度动画过渡时间
    #             )

    #             # 覆盖在整个页面上方（绝对定位）
    #             page.overlay.append(toast)
    #             # 显示动画
    #             toast.opacity = 1
    #             page.update()

    #         if auto_hide:
    #             async def _hide_toast():
    #                 try:
    #                     await asyncio.sleep(duration)  # 异步延迟，不阻塞UI
    #                     toast.opacity = 0
    #                     if toast in page.overlay:
    #                         page.overlay.remove(toast)
    #                     if page:
    #                         page.update()
    #                 except Exception:
    #                     logging.exception("toast hide error")

    #             try:
    #                 page.run_task(_hide_toast)
    #             except Exception:
    #                 logging.exception("toast background error")

    #     except Exception:
    #         logging.exception("toast error")
