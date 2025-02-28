import tkinter as tk
from ttkbootstrap import Window, Button, Entry, Label

root = Window(themename="cosmo")
root.title("登录窗口")
root.geometry("800x600")

# 用户名输入
Label(root, text="用户名").pack(pady=5)
username_entry = Entry(root, bootstyle="info")
username_entry.pack(pady=5)

# 密码输入
Label(root, text="密码").pack(pady=5)
password_entry = Entry(root, show="*", bootstyle="danger")
password_entry.pack(pady=5)

# 登录按钮
login_btn = Button(root, text="登录", bootstyle="success")
login_btn.pack(pady=20)

root.mainloop()
