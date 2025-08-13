# ui_safety.py
import time
import threading
import traceback
import functools
import queue
from typing import Callable, Optional
import logging

import flet as ft

# ------------- configuration -------------
ERROR_THROTTLE_WINDOW = 5.0
ERROR_THROTTLE_LIMIT = 20
HEARTBEAT_INTERVAL = 1.0
HEARTBEAT_TIMEOUT = 3.0
UI_SNAPSHOT_ON_THROTTLE = True

# ------------- global state -------------
_last_heartbeat = time.time()
_error_counts = {}
_error_lock = threading.Lock()
_ui_queue = queue.Queue()
_safety_running = True


# ------------- utilities -------------
def _now():
    return time.time()


# ------------- safe_event wrapper -------------
def safe_event(handler: Callable):
    if not callable(handler):
        raise ValueError("safe_event needs a callable")

    @functools.wraps(handler)
    def wrapper(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except Exception as e:
            logging.error("[UI Error] %s: %s", getattr(handler, "__name__", repr(handler)), e)
            logging.error(traceback.format_exc())

            # find page in args
            page = None
            for a in args:
                if isinstance(a, ft.ControlEvent) and hasattr(a, "page"):
                    page = a.page
                    break
            try:
                if page:
                    # Use new API page.open for SnackBar
                    page.open(ft.SnackBar(ft.Text(f"⚠ 出错: {e}")))
            except Exception:
                logging.exception("failed to show snackbar")
            return None
    return wrapper


# ------------- monkey-patch Control.__setattr__ to auto-wrap on_* handlers -------------
_original_setattr = ft.Control.__setattr__


def _safe_setattr(self, name, value):
    if name.startswith("on_") and callable(value):
        try:
            value = safe_event(value)
        except Exception:
            logging.exception("safe_event wrap failed")
    _original_setattr(self, name, value)


# apply patch once at import
try:
    ft.Control.__setattr__ = _safe_setattr
except Exception:
    logging.exception("failed to monkey-patch ft.Control.__setattr__")


# ------------- safe update wrapper -------------
_original_update = getattr(ft.Control, "update", None)


def _safe_update(self, *args, **kwargs):
    try:
        # if control not attached to page, skip update
        if getattr(self, "page", None) is None:
            logging.warning("[SafeUpdate] %s not attached to page, skip update()", getattr(self, "__repr__", lambda: str(self))())
            return
        return _original_update(self, *args, **kwargs)
    except Exception:
        logging.exception("[SafeUpdate] control.update failed")
        # try to avoid crashing: no re-raise


# apply if update exists
if _original_update is not None:
    try:
        ft.Control.update = _safe_update
    except Exception:
        logging.exception("failed to monkey-patch Control.update")


# ------------- safe invoke for background threads -------------
def safe_invoke_on_page(page: ft.Page, fn: Callable, *args, **kwargs):
    """
    Schedule callable to run on UI thread via page.call_later. If that fails,
    fallback to background queue which will execute job but must not assume UI thread.
    """
    def job():
        try:
            fn(*args, **kwargs)
        except Exception:
            logging.exception("exception while running safe job on page")

    # prefer page.call_later if available
    try:
        page.call_later(lambda _: job())
    except Exception:
        # fallback to queue
        _ui_queue.put(job)


# ------------- background queue consumer (fallback jobs) -------------
def _queue_consumer():
    while _safety_running:
        try:
            job = _ui_queue.get(timeout=1.0)
        except Exception:
            continue
        try:
            job()
        except Exception:
            logging.exception("exception in ui fallback job")


_consumer_thread = threading.Thread(target=_queue_consumer, daemon=True)
_consumer_thread.start()


# ------------- global on_event handler (error limit & snapshot) -------------
def _global_on_event(e: ft.ControlEvent, page: Optional[ft.Page] = None):
    try:
        if getattr(e, "name", None) == "error":
            err = str(getattr(e, "data", ""))
            logging.error("Received Flutter error event: %r", err)

            with _error_lock:
                now = _now()
                lst = _error_counts.get(err) or []
                # keep only recent
                lst = [t for t in lst if now - t <= ERROR_THROTTLE_WINDOW]
                lst.append(now)
                _error_counts[err] = lst

                if len(lst) > ERROR_THROTTLE_LIMIT:
                    # logging.warning("Error %r occurred %d times in %.1fs — throttle activated", err, len(lst), ERROR_THROTTLE_WINDOW)
                    if UI_SNAPSHOT_ON_THROTTLE and page is not None:
                        logging.error('page is none')
                    # drop further processing
                    return
            # normal flow - log once
            logging.error("[Flutter Error] %s", err)
    except Exception:
        logging.exception("exception in global on_event")


# ------------- heartbeat monitor -------------
def _start_heartbeat(page: ft.Page, interval=HEARTBEAT_INTERVAL, timeout=HEARTBEAT_TIMEOUT):
    def hb():
        global _last_heartbeat
        while _safety_running:
            time.sleep(interval)
            idle = time.time() - _last_heartbeat
            if idle > timeout:
                logging.warning("Heartbeat: page.update() not called for %.1fs — saving snapshot", idle)

    t = threading.Thread(target=hb, daemon=True)
    t.start()


# ------------- page.update wrapper to update heartbeat -------------
def _wrap_page_update(page: ft.Page):
    orig = getattr(page, "update", None)
    if not orig:
        return

    def _wrapped(*args, **kwargs):
        global _last_heartbeat
        try:
            _last_heartbeat = time.time()
            return orig(*args, **kwargs)
        except Exception:
            logging.exception("page.update raised exception")
    try:
        page.update = _wrapped
    except Exception:
        logging.exception("failed to wrap page.update")


# ------------- initializer to hook page ----------------
def init_ui_safety(page: ft.Page):
    """
    Call this at very start of your main(page) to enable protections.
    Example:
        def main(page):
            init_ui_safety(page)
            ...
    """
    # wrap update
    _wrap_page_update(page)

    # hook page.on_event (preserve old)
    try:
        orig = getattr(page, "on_event", None)

        def _on_event(e):
            try:
                _global_on_event(e, page)
            except Exception:
                logging.exception("global on_event handler error")
            if callable(orig):
                try:
                    orig(e)
                except Exception:
                    logging.exception("orig on_event raised")
        page.on_event = _on_event
    except Exception:
        logging.exception("failed to set page.on_event")

    # start heartbeat
    _start_heartbeat(page)
    logging.info("ui_safety initialized")
