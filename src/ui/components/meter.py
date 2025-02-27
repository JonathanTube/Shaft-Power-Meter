import tkinter as tk
from tkchart import LineChart

root = tk.Tk()

chart = LineChart(
    root,
    width=500,
    height=300,
    x_axis_values=(1, 2, 3),
    y_axis_start=0,
    y_axis_end=10
)
line = chart.create_line("示例线", color="red")
chart.display(line, [2, 5, 8])  # 静态数据
chart.pack()

root.mainloop()
