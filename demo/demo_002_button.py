from ttkbootstrap import Window, Button  # 使用 ttkbootstrap 的增强组件

# 初始化窗口并选择主题（例如 'darkly'）
root = Window(themename="darkly")
root.title("TtkBootstrap Demo")
root.geometry("800x600")


# 创建不同风格的按钮
btn1 = Button(root, text="Primary", bootstyle="primary")
btn1.pack(pady=10)

btn2 = Button(root, text="Success", bootstyle="success")
btn2.pack(pady=10)

btn3 = Button(root, text="Danger", bootstyle="danger")
btn3.pack(pady=10)

btn_primary = Button(root, text="主要按钮", bootstyle="primary")  # 蓝色按钮
btn_primary.pack(pady=10)  # 垂直布局，设置间距

btn_danger = Button(root, text="危险操作", bootstyle="danger-outline")  # 红色边框按钮
btn_danger.pack(pady=10)

root.mainloop()
