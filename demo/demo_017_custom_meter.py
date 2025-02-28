from ttkbootstrap import Window
import tkinter as tk

root = Window(themename="cosmo")
root.geometry("600x400")

canvas = tk.Canvas(root, width=300, height=300, bg="white")
canvas.pack(pady=20)

# 基础参数
center_x, center_y = 150, 150  # 圆心
radius = 120                   # 圆弧半径
arc_span = 270                 # 3/4 圆的总跨度（degrees）

# 绘制三色空心圆弧


def draw_hollow_arc():
    # 绿色的 80% 部分（216 度）
    canvas.create_arc(
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius,
        start=0,                # 起始角度调整为顶部（12点方向为90度）
        extent=216,              # 216度 = 270 * 0.8
        style="arc",             # 空心圆弧（非扇形）
        outline="#00ff00",       # 绿色
        width=40
    )
    # 黄色的 10% 部分（27 度）
    canvas.create_arc(
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius,
        start=216 - 27,          # 接续绿色结束位置（0+216=306度）
        extent=27,               # 27度 = 270 * 0.1
        style="arc",
        outline="#ffff00",       # 黄色
        width=40
    )
    # 红色的余下 10% 部分（实际=270-216-27=27度）
    canvas.create_arc(
        center_x - radius,
        center_y - radius,
        center_x + radius,
        center_y + radius,
        start=360 - 27 - 27,
        extent=27,               # 最终27度刚好补满270
        style="arc",
        outline="#ff0000",       # 红色
        width=40
    )


draw_hollow_arc()

root.mainloop()
