from customtkinter import CTkFrame
import tkinter.ttk as ttk
from config import TABLE_WIDTH_STOCK_CODE, TABLE_WIDTH_STOCK_NAME
from config import TABLE_STOCK_CODE, TABLE_STOCK_NAME

class MagicNineView(CTkFrame):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

        # 不使用 Treeview 控件提供的表头
        self.table = ttk.Treeview(self, show='headings', height=5)
        # 自定义表头
        columns = {
            TABLE_STOCK_CODE: TABLE_WIDTH_STOCK_CODE, 
            TABLE_STOCK_NAME: TABLE_WIDTH_STOCK_NAME,
        }
        # 批量设置表头标题
        self.table['columns'] = list(columns)
        for c in columns:
            self.table.heading(c, text = c)
            self.table.column(c, width = columns[c], anchor='center')          
        self.table.pack()
