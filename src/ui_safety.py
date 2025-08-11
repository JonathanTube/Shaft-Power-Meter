# ui_safety.py
import traceback
import logging
import functools
import flet as ft


def safe_event(handler):
    """
    安全事件包装器：防止回调异常导致整个UI卡死
    """
    if not callable(handler):
        raise ValueError("safe_event 需要一个函数或方法")

    @functools.wraps(handler)
    def wrapper(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except Exception as e:
            logging.error(f"[UI Error] {handler.__name__}: {e}")
            logging.error(traceback.format_exc())

            # 如果事件有 page 参数，弹出提示
            page = None
            for arg in args:
                if isinstance(arg, ft.ControlEvent) and hasattr(arg, "page"):
                    page = arg.page
                    break
            if page:
                try:
                    page.open(ft.SnackBar(ft.Text(f"⚠ 出错: {e}")))
                    page.update()
                except:
                    pass
            return None

    return wrapper


# 全局事件安全补丁
_original_setattr = ft.Control.__setattr__


def safe_setattr(self, name, value):
    if name.startswith("on_") and callable(value):
        value = safe_event(value)
    _original_setattr(self, name, value)


ft.Control.__setattr__ = safe_setattr


# -------- 安全 UI 更新补丁 --------
_original_update = ft.Control.update

def safe_update(self, *args, **kwargs):
    try:
        if getattr(self, "page", None):  # 确保控件挂在页面上
            return _original_update(self, *args, **kwargs)
        else:
            logging.warning(f"[SafeUpdate] {self} 没有挂在页面上，跳过 update()")
    except Exception as e:
        logging.error(f"[SafeUpdate] 控件更新失败: {e}")
        logging.error(traceback.format_exc())

ft.Control.update = safe_update