import customtkinter as ctk

def on_closing():
    print("CTkToplevel window is closing")
    # 在这里添加你需要执行的代码
    # 例如，你可以在这里进行资源清理或保存数据等操作
    toplevel.destroy()  # 确保窗口被销毁

app = ctk.CTk()
toplevel = ctk.CTkToplevel(app)

# 使用 protocol 方法绑定 WM_DELETE_WINDOW 事件到 on_closing 函数
toplevel.protocol("WM_DELETE_WINDOW", on_closing)

app.mainloop()
