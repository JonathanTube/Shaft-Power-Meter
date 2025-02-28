from ttkbootstrap import Window, Progressbar

root = Window(themename="cosmo")
root.geometry("800x600")

# 进度条（支持动态更新）
progress = Progressbar(root, maximum=100, bootstyle="striped-success")
progress.pack(pady=5)
progress.start(10)  # 模拟进度动画

root.mainloop()
