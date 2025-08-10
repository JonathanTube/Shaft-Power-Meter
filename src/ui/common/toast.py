import logging
import time

import flet as ft


class Toast:
    @staticmethod
    def show_success(page: ft.Page, message: str = None):
        if page is None or page.session is None:
            return

        msg = message if message is not None else page.session.get("lang.toast.success")
        Toast.show_toast(page, msg, ft.Colors.GREEN_500, ft.Colors.WHITE)

    @staticmethod
    def show_warning(page: ft.Page, message: str = None):
        if page is None or page.session is None:
            return
        msg = message if message is not None else page.session.get("lang.toast.warning")
        Toast.show_toast(page, msg, ft.Colors.ORANGE_500, ft.Colors.WHITE)

    @staticmethod
    def show_error(page: ft.Page, message: str = None, auto_hide: bool = True):
        if page is None or page.session is None:
            return
        msg = message if message is not None else page.session.get("lang.toast.error")
        Toast.show_toast(page, msg, ft.Colors.RED_500, ft.Colors.WHITE, auto_hide=auto_hide)

    @staticmethod
    def show_toast(page: ft.Page, message: str, bg_color: ft.Colors, color: ft.Colors, duration=2, auto_hide: bool = True):
        try:
            if page and page.overlay:
                # 创建 Toast 控件
                toast = ft.Container(
                    expand=True,
                    content=ft.Row(
                        expand=False,
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
                # 显示动画
                toast.opacity = 1
                page.update()

            # -- 在 Toast.show_toast 中，替换 auto_hide 部分为：
            if auto_hide:
                def _hide_toast(p: ft.Page):
                    try:
                        time.sleep(duration)  # 这个 sleep 在后台线程执行，不会阻塞主线程
                        try:
                            toast.opacity = 0
                            if toast in p.overlay:
                                p.overlay.remove(toast)
                            p.update()
                        except Exception:
                            logging.exception("toast hide error")
                    except Exception:
                        logging.exception("toast background error")

                # 用 page.run_task 在后台线程执行 _hide_toast
                try:
                    page.run_task(_hide_toast, page)
                except Exception:
                    # 如果 run_task 不可用或失败，降级为线程（保底）
                    import threading
                    threading.Thread(target=_hide_toast, args=(page,), daemon=True).start()

        except:
            logging.exception("toast error")
