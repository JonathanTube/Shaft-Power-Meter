from ttkbootstrap import Window, Combobox

root = Window(themename="cosmo")
root.geometry("800x600")

# 高级组件示例
combobox = Combobox(root, values=["选项1", "选项2"], bootstyle="default")
combobox.pack(pady=10)

root.mainloop()
