import tkinter as tk
import ctypes
from ttkbootstrap import Style, Window, Separator
from src.ui.components.header import Header


class PLCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shaft Power Meter")
        self.root.geometry("1280x800")  # Set window resolution

        # root.overrideredirect(True)  # True 表示无边框窗口
        # # 设置拖拽区域（例如整个窗口背景）
        # root.bind("<ButtonPress-1>", self.start_move)  # 鼠标左键按下
        # root.bind("<B1-Motion>", self.do_move)        # 按住左键拖拽

        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # 优先级：系统 DPI 感知
        root.tk.call('tk', 'scaling', 2.0)  # 调整值直到显示清晰（通常 1.5~2.5）

        # Create UI elements
        self.create_widgets()

    def create_widgets(self):
        # Create header
        Header(self.root)
        # Create horizontal line
        Separator().pack(fill='x')

    def on_switch_change(self):
        self.root.style.theme_use("dark")

    # 手动拖拽窗口移动功能
    def start_move(self, event):
        self.root.x = event.x
        self.root.y = event.y

    def do_move(self, event):
        self.root.geometry(f"+{event.x_root - root.x}+{event.y_root - root.y}")


if __name__ == "__main__":
    root = Window(themename="darkly")
    app = PLCApp(root)
    root.mainloop()
