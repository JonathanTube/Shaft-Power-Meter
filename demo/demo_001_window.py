from ttkbootstrap import Window  # 使用 ttkbootstrap 的增强组件

# 初始化窗口并选择主题（例如 'darkly'）
root = Window(themename="darkly")
root.title("TtkBootstrap Demo")
root.geometry("800x600")


root.mainloop()  # 进入消息循环
