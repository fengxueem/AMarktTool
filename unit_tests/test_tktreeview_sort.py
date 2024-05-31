# Treeview中点击表头排序
import tkinter
from tkinter import ttk
 
# 初始化窗口
win = tkinter.Tk()
win.title("Tkinter Treeview 实例")  # 窗口标题
win.geometry("453x127")  # 窗口的宽度和高度
 
# 排序
def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    print(f'tv.get_children():{tv.get_children("")}')
    print(f'l:{l}')
    # 传入带单位的流量（MB/GB）计算并返回统计的单位（这里是 MB）以进行统一的数字大小排序
    # 如果对计算有精度需求或对其他单位也有需求如 B、KB、TB 等可以自行学习并增加
    MB_To_MB = lambda Traffic: int(Traffic.replace(' MB', '')) if 'MB' in Traffic else 0  # 这里只考虑 GB 和 MB 两种情况
    GB_To_MB = lambda Traffic: int(Traffic.replace(' GB', '')) * 1024 if 'GB' in Traffic else MB_To_MB(Traffic)
    if 'MB' in l[0][0] or 'GB' in l[0][0]:
        # 如果第一行的数据里存在 'MB' 或 'GB' 的文本（如果第一行没有的话会引发 BUG，我没想到其他的方法了）
        l.sort(key=lambda t: GB_To_MB(t[0]), reverse=reverse)  # 对流量进行转统一单位的数字后再排序
    elif 'cm' in l[0][0]:
        # 如果第一行的数据里存在 '元' 的文本
        l.sort(key=lambda t: int(t[0].replace(' cm', '')), reverse=reverse)  # 把单位去除后转数字再排序
    elif '元' in l[0][0]:
        # 如果第一行的数据里存在 '元' 的文本
        l.sort(key=lambda t: int(t[0].replace(' 元', '')), reverse=reverse)  # 把单位去除后转数字再排序
    else:
        try:
            # 优先尝试数字排序
            l.sort(key=lambda t: int(t[0]), reverse=reverse)
        except:
            # 出错则普遍排序
            l.sort(reverse=reverse)
            # 这种排序根据首位字符来排序，不适合数字，会出现：1,11,2 这种不符合从大到小或从小到大的排序
    print(l)
    # 移动数据
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))
 
 
# 初始化表格
tree = ttk.Treeview(win, show="headings", height=5)  # 创建表格对象，show="headings" 为隐藏首列，height 为表格高度（行）
columns = {
    'ID': 50,
    '昵称': 100,
    '身高': 100,
    '余额': 100,
    '流量': 100
}  # 列头标题和对应的宽度，随便增删改查
tree['columns'] = list(columns)  # 批量设置列头标题
for column in columns:  # 批量设置列属性
    tree.heading(column, text=column)  # #设置列标题
    tree.column(column, width=columns[column], anchor='center')  # 设置列酷安，anchor 为锚点，'center' 表示中央居中
    # 也可以用方位词东南西北的英文缩写表示，即 N(North, 北): 上中对齐、SW(South West, 西南)：左下对齐
    # tree.column(column, width=columns[column], anchor=tkinter.SW)  # 示例，只改 SW 就行
    # anchor: n, ne, e, se, s, sw, w, nw, or center
    tree.heading(column, command=lambda _col=column: treeview_sort_column(tree, _col, False))  # 设置点击执行排序操作
 
Data = [
    [1, '张三', '184 cm', '2000 元', '500 MB'],
    [2, '李四', '170 cm', '100 元', '10 GB'],
    [3, '王五', '175 cm', '-300 元', '-200 MB']
]  # 要导入表格的数据，这里引入单位，待会对不同的单位进行排序
 
# 遍历并导入
for person in Data:
    tree.insert('', person[0], text='', values=person)
 
tree.pack()
win.mainloop()  # 使窗口可视化