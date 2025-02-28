from ttkbootstrap import Style, Window, Button  # 使用 ttkbootstrap 的增强组件

# 初始化窗口并选择主题（例如 'darkly'）
root = Window(themename="darkly")
root.title("TtkBootstrap Demo")
root.geometry("800x600")


style = Style()


def change_theme():
    style.theme_use("solar")  # 变为 solar 主题


# 添加切换主题的按钮
theme_btn = Button(root, text="切换主题", command=change_theme)
theme_btn.pack(pady=20)


root.mainloop()
