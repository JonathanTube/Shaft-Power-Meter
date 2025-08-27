import threading
import os
import sys
import logging
import webbrowser
from typing import Optional


_icon = None
_icon_thread: Optional[threading.Thread] = None
_running = False


def _get_icon_image(icon_path: str):
    try:
        from PIL import Image
        return Image.open(icon_path)
    except Exception:
        logging.exception("failed to load tray icon image: %s", icon_path)
        return None


def _resolve_asset_path(relative_path: str) -> str:
    """
    Resolve an asset path for both dev and frozen (PyInstaller) environments.
    """
    if getattr(sys, 'frozen', False):
        # In packaged exe, assets folder is next to the executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # In dev, assets folder is under project src
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, relative_path)


def start_tray(app_name: str, url: str, icon_rel_path: str = 'assets/icon.png'):
    """
    Start a Windows system tray icon with menu to open UI and exit.
    Safe no-op on platforms without pystray or in headless environments.
    """
    global _icon, _icon_thread, _running
    if _running:
        return

    try:
        import pystray
        from pystray import MenuItem as item, Menu
    except Exception:
        logging.warning("pystray not available; skipping tray icon")
        return

    icon_path = _resolve_asset_path(icon_rel_path)
    image = _get_icon_image(icon_path)
    if image is None:
        logging.warning("tray icon image not found: %s", icon_path)

    def on_open():
        try:
            webbrowser.open(url)
        except Exception:
            logging.exception("failed to open browser for %s", url)

    def on_exit(icon, item_):
        try:
            stop_tray()
        except Exception:
            pass
        # Hard exit process to stop background server
        os._exit(0)

    menu = Menu(
        item("Open UI", lambda: on_open()),
        item("Exit", lambda: on_exit(_icon, None))
    )

    _icon = pystray.Icon(app_name, image, app_name, menu)

    def run_icon():
        try:
            _icon.run()
        except Exception:
            logging.exception("tray icon crashed")

    _icon_thread = threading.Thread(target=run_icon, daemon=True)
    _icon_thread.start()
    _running = True


def stop_tray():
    global _icon, _icon_thread, _running
    if not _running:
        return
    try:
        if _icon is not None:
            _icon.stop()
    except Exception:
        pass
    _icon = None
    _icon_thread = None
    _running = False

