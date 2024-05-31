import tkinter as tk
from tkinter import ttk

# 创建主窗口
window = tk.Tk()

# 创建Treeview部件
tree = ttk.Treeview(window, show='headings')
tree.pack()
columns = {
        'a' : [120],
        'b' : [120], 
    }
# 批量设置表头标题
tree['columns'] = list(columns)
for c in columns:
    # 设置表头文字
    tree.heading(c, text = c)
    # 设置当前列宽度与其他格式
    tree.column(c, minwidth = columns[c][0], anchor='center')
# 向Treeview部件中添加项目
tree.insert("", "end", values=("Item 1", "1"))
tree.insert("", "end", values=("Item 2", "1"))
tree.insert("", "end", values=("Item 3", "1"))

def show_details(event):
    item_id = tree.focus()
    item_text = tree.item(item_id)["values"]
    print(f'item_id:{item_id}, item_text:{item_text}')
    if item_text == "Item 1":
        details = "This is item 1, it has sub-items: Item 1a and Item 1b."
    elif item_text == "Item 2":
        details = "This is item 2."
    else:
        details = "No details available for this item."

    details_label.config(text=details)

# 创建一个用于显示项目详情的标签部件
details_label = tk.Label(window, text="Select an item to see details")
details_label.pack()

# 将show_details函数绑定到Treeview部件的点击事件上
tree.bind("<<TreeviewSelect>>", show_details)

# 运行主窗口的事件循环
window.mainloop()
