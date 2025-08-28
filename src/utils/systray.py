import asyncio
import threading
import os
import sys
import logging
import webbrowser
from typing import Optional

from utils.system_exit_tool import SystemExitTool

_icon: Optional[object] = None
_icon_thread: Optional[threading.Thread] = None
_running = False


def _get_icon_image(path: str):
    """加载托盘图标"""
    try:
        from PIL import Image
        return Image.open(path)
    except Exception:
        logging.exception("加载托盘图标失败: %s", path)
        return None


def _resolve_asset_path(rel_path: str) -> str:
    """解析资源路径"""
    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) \
        else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, rel_path)


def _open_ui():
    """打开本地UI页面"""
    try:
        webbrowser.open('localhost')
    except Exception:
        logging.exception("打开浏览器访问 localhost 失败")


def _exit():
    """退出程序"""
    try:
        asyncio.run(SystemExitTool.exit_app())
    except Exception:
        pass
    stop_tray()


def _restart():
    """重启程序"""
    try:
        asyncio.run(SystemExitTool.exit_app())
    except Exception:
        pass
    stop_tray()
    # 重新启动应用
    python = sys.executable
    os.execl(python, python, *sys.argv)


def start_tray():
    """启动 Windows 托盘图标，包含‘打开 UI’、‘重启’和‘退出’选项"""
    global _icon, _icon_thread, _running
    if _running:
        return

    try:
        import pystray
        from pystray import MenuItem as item, Menu
    except ImportError:
        logging.warning("未安装 pystray，跳过托盘图标")
        return

    image = _get_icon_image(_resolve_asset_path("assets/icon.ico"))
    if image is None:
        logging.warning("未找到托盘图标图片")

    menu = Menu(
        item("Open", lambda: _open_ui()),
        # item("Reboot", lambda: _restart()),
        item("Exit", lambda: _exit())
    )
    _icon = pystray.Icon("Shaft Power Meter", image, "Shaft Power Meter", menu)

    _icon_thread = threading.Thread(target=_icon.run, daemon=True)
    _icon_thread.start()
    _running = True


def stop_tray():
    """停止托盘图标"""
    global _icon, _icon_thread, _running
    if not _running:
        return
    try:
        _icon.stop()
    except Exception:
        pass
    _icon = None
    _icon_thread = None
    _running = False
