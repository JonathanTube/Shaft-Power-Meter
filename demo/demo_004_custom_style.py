from ttkbootstrap import Style, Window, Button  # 使用 ttkbootstrap 的增强组件

# 初始化窗口并选择主题（例如 'darkly'）
root = Window(themename="darkly")
root.title("TtkBootstrap Demo")
root.geometry("800x600")


style = Style()
# 修改默认按钮的字体和颜色; 这里会影响所有的按钮
style.configure("TButton", font=("微软雅黑", 12), foreground="white")

# 创建自定义样式（例如：金色按钮），这里可以追加自己的样式
style.configure("Gold.TButton", background="gold", bordercolor="red")
custom_btn = Button(root, text="自定义按钮", style="Gold.TButton")
custom_btn.pack(pady=10)

root.mainloop()
