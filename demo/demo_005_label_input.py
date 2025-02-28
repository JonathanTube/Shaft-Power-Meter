
from ttkbootstrap import Window, Label, Entry

root = Window(themename="darkly")
root.title("TtkBootstrap Demo")
root.geometry("800x600")

Label(root, text="用户名：").pack(pady=5)
Entry(root, bootstyle="info").pack(pady=5)  # 青色输入框

root.mainloop()
