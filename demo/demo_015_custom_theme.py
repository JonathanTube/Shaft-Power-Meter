
from ttkbootstrap import Window, Style

root = Window(themename="cosmo")
root.geometry("800x600")

style = Style(theme="darkly")

# 修改所有按钮的默认内边距
style.configure("TButton", padding=10)

# 创建自定义主题变体（如：深绿色为主题的 darkly）
style.colors.update({
    "primary": "#2d5a27",  # 覆盖原主题的主色
    "danger": "#ff4444"     # 设置新的危险色
})

# 重新应用更新后的主题
style.theme_update()

root.mainloop()
