from ttkbootstrap.dialogs import Messagebox, Querybox
from ttkbootstrap import Window

root = Window(themename="cosmo")
root.geometry("800x600")


# 信息提示框
Messagebox.show_info("操作成功", "您的文件已保存！", parent=root)

# 确认对话框
result = Messagebox.show_question("确认删除吗？", "警告", parent=root)
if result == "是":
    print("执行删除操作")

# 输入对话框
user_input = Querybox.get_string("请输入用户名", "登录", parent=root)
print(f"用户输入：{user_input}")


root.mainloop()
