import flet as ft
import time, traceback, threading, json
from functools import wraps

# ===== 全局监控变量 =====
_last_event = None
_last_event_time = time.time()
_last_heartbeat = time.time()

def _log(msg):
    print(f"[DEBUG][{time.strftime('%H:%M:%S')}] {msg}")

# ===== 包装 page.update() =====
def _wrap_update(page):
    orig_update = page.update

    @wraps(orig_update)
    def safe_update(*args, **kwargs):
        global _last_heartbeat
        _last_heartbeat = time.time()
        return orig_update(*args, **kwargs)

    page.update = safe_update

# ===== 包装事件处理器 =====
def _wrap_handler(func):
    if not callable(func):
        return func

    @wraps(func)
    def wrapper(*args, **kwargs):
        global _last_event, _last_event_time
        _last_event = func.__name__
        _last_event_time = time.time()
        _log(f"事件触发: {_last_event}")
        try:
            return func(*args, **kwargs)
        except Exception:
            traceback.print_exc()
            raise
    return wrapper

# ===== 包装 page 上的事件 =====
def _wrap_all_handlers(page):
    for name, val in vars(page).items():
        if callable(val) and name.startswith("on_"):
            setattr(page, name, _wrap_handler(val))
    for ctl in page.controls:
        for attr in dir(ctl):
            if attr.startswith("on_"):
                try:
                    handler = getattr(ctl, attr)
                    if callable(handler):
                        setattr(ctl, attr, _wrap_handler(handler))
                except:
                    pass

# ===== 控件树快照 =====
def _save_ui_snapshot(page):
    try:
        def serialize(ctrl):
            return {
                "type": ctrl.__class__.__name__,
                "props": {k: str(v) for k, v in ctrl.__dict__.items() if not k.startswith("_")},
                "children": [serialize(c) for c in getattr(ctrl, "controls", [])]
            }
        with open("ui_snapshot.json", "w", encoding="utf-8") as f:
            json.dump(serialize(page), f, ensure_ascii=False, indent=2)
        _log("UI 快照已保存到 ui_snapshot.json")
    except Exception as e:
        _log(f"保存 UI 快照失败: {e}")

# ===== 心跳线程 =====
def _start_heartbeat(page):
    def heartbeat():
        while True:
            time.sleep(1)
            diff = time.time() - _last_heartbeat
            if diff > 2:  # 超过 2 秒没 update
                _log(f"⚠ 检测到 UI 卡死 {diff:.1f}s，最后事件: {_last_event} ({time.time() - _last_event_time:.1f}s 前)")
                _save_ui_snapshot(page)
    threading.Thread(target=heartbeat, daemon=True).start()

# ===== 初始化调试器 =====
def init_debug(page):
    _wrap_update(page)
    _wrap_all_handlers(page)
    _start_heartbeat(page)
    _log("调试器已启动")
