import tkinter as tk
from ttkbootstrap import Window, Notebook, Label

root = Window(themename="minty")
root.title("TtkBootstrap Demo")
root.geometry("800x600")

# 添加 Notebook 选项卡（类似现代浏览器标签）
notebook = Notebook(root)

# 创建第一个选项卡
tab1 = tk.Frame(notebook)
tab1.pack(fill='both', expand=True)  # Set fill and expand properties

label1 = Label(tab1, text="This is a label")
label1.pack()

notebook.add(tab1, text="Tab 1")

# 创建第二个选项卡
tab2 = tk.Frame(notebook)
tab2.pack(fill='both', expand=True)  # Set fill and expand properties
notebook.add(tab2, text="Tab 2")

# 创建第三个选项卡
tab3 = tk.Frame(notebook)
tab3.pack(fill='both', expand=True)  # Set fill and expand properties
notebook.add(tab3, text="Tab 3")

# 设置默认选中的选项卡
notebook.select(tab1)

# 将选项卡添加到窗口中
# Set fill and expand properties
notebook.pack(padx=10, pady=10, fill='both', expand=True)

root.mainloop()
