from customtkinter import CTkFrame, CTkScrollbar
import tkinter.ttk as ttk
from config import TABLE_WIDTH_STOCK_CODE, TABLE_WIDTH_STOCK_NAME
from config import TABLE_STOCK_CODE, TABLE_STOCK_NAME

class MagicNineView(CTkFrame):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

        # 不使用 Treeview 控件提供的表头
        self.table = ttk.Treeview(self, show='headings')
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
        self.table.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        # 创建垂直滚动条
        self.scrollbar = CTkScrollbar(self)
        self.scrollbar.grid(row=0, column=1, sticky='nsw')
        
        # 关联滚动条和表格
        self.table.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.table.yview)
