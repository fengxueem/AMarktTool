from customtkinter import CTkFrame, CTkScrollbar
import tkinter.ttk as ttk
from config import TABLE_STOCK_INDEX, TABLE_STOCK_CODE, TABLE_STOCK_NAME
from config import TABLE_WIDTH_STOCK_INDEX, TABLE_WIDTH_STOCK_CODE, TABLE_WIDTH_STOCK_NAME

class MagicNineView(CTkFrame):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

        # 创建垂直滚动条
        self.scrollbar = CTkScrollbar(master = self, orientation= 'vertical')
        
        # 不使用 Treeview 控件提供的表头
        self.table = ttk.Treeview(
            master = self,
            show='headings',
            yscrollcommand=self.scrollbar.set
            )
        # 自定义表头
        columns = {
            TABLE_STOCK_INDEX : TABLE_WIDTH_STOCK_INDEX,
            TABLE_STOCK_CODE : TABLE_WIDTH_STOCK_CODE, 
            TABLE_STOCK_NAME : TABLE_WIDTH_STOCK_NAME,
        }
        # 批量设置表头标题
        self.table['columns'] = list(columns)
        for c in columns:
            self.table.heading(c, text = c)
            self.table.column(c, width = columns[c], anchor='center')          
        
        # 关联滚动条和表格
        self.scrollbar.configure(command=self.table.yview)
        # 设置滚动条和表格的布局
        # 先放置滚动条
        self.scrollbar.pack(side='right', fill='y')
        # 再让表格填充剩下区域
        self.table.pack(fill='both', expand=True)