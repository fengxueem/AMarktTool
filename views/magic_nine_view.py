from customtkinter import CTkFrame, CTkScrollbar
import tkinter.ttk as ttk
from config import TABLE_INDEX, TABLE_STOCK_CODE, TABLE_STOCK_NAME, TABLE_SIGNAL_DATE
from config import TABLE_WIDTH_INDEX, TABLE_WIDTH_STOCK_CODE, TABLE_WIDTH_STOCK_NAME, TABLE_WIDTH_SIGNAL_DATE

class MagicNineView(CTkFrame):
    
    @staticmethod
    def table_sort_index(table, col, is_reverse_order):
        lines = [(table.set(k, col), k) for k in table.get_children('')]
        lines.sort(key=lambda t: int(t[0]), reverse=is_reverse_order)
        # 移动数据
        for index, (_, key) in enumerate(lines):
            table.move(key, '', index)
        # 下一次点击表头时，使用相反的顺序排序
        table.heading(col, command=lambda: MagicNineView.table_sort_index(table, col, not is_reverse_order))
    
    @staticmethod
    def table_sort_stock_code(table, col, is_reverse_order):
        lines = [(table.set(k, col), k) for k in table.get_children('')]
        lines.sort(key=lambda t: int(t[0]), reverse=is_reverse_order)
        # 移动数据
        for index, (_, key) in enumerate(lines):
            table.move(key, '', index)
        # 下一次点击表头时，使用相反的顺序排序
        table.heading(col, command=lambda: MagicNineView.table_sort_stock_code(table, col, not is_reverse_order))
    
    @staticmethod
    def table_sort_signal_date(table, col, is_reverse_order):
        lines = [(table.set(k, col), k) for k in table.get_children('')]
        lines.sort(key=lambda t: int(t[0].replace('-', '')), reverse=is_reverse_order)
        # 移动数据
        for index, (_, key) in enumerate(lines):
            table.move(key, '', index)
        # 下一次点击表头时，使用相反的顺序排序
        table.heading(col, command=lambda: MagicNineView.table_sort_signal_date(table, col, not is_reverse_order))
    
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

        # 创建垂直滚动条
        self.scrollbar = CTkScrollbar(master = self, orientation= 'vertical')
        
        # 创建表格
        self.table = ttk.Treeview(
            master = self,
            show='headings', # 隐藏表格默认的首列
            yscrollcommand=self.scrollbar.set # 关联表格 -> 滚动条
            )
        # 自定义每列 最小宽度 和 排序方法
        columns = {
            TABLE_INDEX : [TABLE_WIDTH_INDEX, MagicNineView.table_sort_index],
            TABLE_STOCK_CODE : [TABLE_WIDTH_STOCK_CODE, MagicNineView.table_sort_stock_code], 
            TABLE_STOCK_NAME : [TABLE_WIDTH_STOCK_NAME],
            TABLE_SIGNAL_DATE : [TABLE_WIDTH_SIGNAL_DATE, MagicNineView.table_sort_signal_date]
        }
        # 批量设置表头标题
        self.table['columns'] = list(columns)
        for c in columns:
            # 设置表头文字
            self.table.heading(c, text = c)
            # 设置当前列宽度与其他格式
            self.table.column(c, minwidth = columns[c][0], anchor='center')
            # 如果当前列存在排序方法，则将其添加
            if len(columns[c]) > 1:
                sort_func = columns[c][1]
                self.table.heading(c, command=lambda _col=c: sort_func(self.table, _col, False))      
        
        # 关联滚动条 -> 表格 
        self.scrollbar.configure(command=self.table.yview)
        # 设置滚动条和表格的布局
        # 先放置滚动条
        self.scrollbar.pack(side='right', fill='y')
        # 再让表格填充剩下区域
        self.table.pack(fill='both', expand=True)
    