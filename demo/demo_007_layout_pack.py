import tkinter as tk

from ttkbootstrap import Notebook
from ttkbootstrap import Window, Button

root = Window(themename="darkly")
root.title("TtkBootstrap Demo")
root.geometry("800x600")

btn1 = Button(root, text="btn1", bootstyle="primary")
btn2 = Button(root, text="btn2", bootstyle="primary")
btn3 = Button(root, text="btn3", bootstyle="primary")
btn4 = Button(root, text="btn4", bootstyle="primary")
btn5 = Button(root, text="btn5", bootstyle="primary")

# 用 grid 实现网格布局
btn1.pack(pady=10, fill='x')
btn2.pack(pady=10)
btn3.pack(pady=10)

root.mainloop()
