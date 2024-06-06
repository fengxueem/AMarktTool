from config import MAGIC_NINE_FRAME
from config import MAGIC_NINE_BTN, MAGIC_NINE_BTN_DISABLED
from config import TABLE_INDEX, TABLE_STOCK_CODE, TABLE_SIGNAL_DATE
from models import Model
from views import View

import threading
from .__base__ import BaseController

class MagicNineController(BaseController):
    
    @staticmethod
    def table_sort_index(table, col, is_reverse_order):
        lines = [(table.set(k, col), k) for k in table.get_children('')]
        lines.sort(key=lambda t: int(t[0]), reverse=is_reverse_order)
        # 移动数据
        for index, (_, key) in enumerate(lines):
            table.move(key, '', index)
        # 下一次点击表头时，使用相反的顺序排序
        table.heading(col, command=lambda: MagicNineController.table_sort_index(table, col, not is_reverse_order))
    
    @staticmethod
    def table_sort_stock_code(table, col, is_reverse_order):
        lines = [(table.set(k, col), k) for k in table.get_children('')]
        lines.sort(key=lambda t: int(t[0]), reverse=is_reverse_order)
        # 移动数据
        for index, (_, key) in enumerate(lines):
            table.move(key, '', index)
        # 下一次点击表头时，使用相反的顺序排序
        table.heading(col, command=lambda: MagicNineController.table_sort_stock_code(table, col, not is_reverse_order))
    
    @staticmethod
    def table_sort_signal_date(table, col, is_reverse_order):
        lines = [(table.set(k, col), k) for k in table.get_children('')]
        lines.sort(key=lambda t: int(t[0].replace('-', '')), reverse=is_reverse_order)
        # 移动数据
        for index, (_, key) in enumerate(lines):
            table.move(key, '', index)
        # 下一次点击表头时，使用相反的顺序排序
        table.heading(col, command=lambda: MagicNineController.table_sort_signal_date(table, col, not is_reverse_order))
    
    def show_stock_detail(self, event):
        magic_nine_table = self.frame.table
        item_id = magic_nine_table.focus()
        item_text = magic_nine_table.item(item_id)["values"]
        stock_code = str(item_text[1]).zfill(6)
        self.mediator.notify(self, "OPEN_STOCK_DETAIL_WINDOWS", stock_code)
    
    def __init__(self, view : View, model : Model) -> None:
        self.view = view
        self.model = model
        self.frame = self.view.frames[MAGIC_NINE_FRAME]
        # 自定义表格每列排序方法
        columns = {
            TABLE_INDEX : [MagicNineController.table_sort_index],
            TABLE_STOCK_CODE : [MagicNineController.table_sort_stock_code],
            TABLE_SIGNAL_DATE : [MagicNineController.table_sort_signal_date]
        }
        magic_nine_table = self.frame.table
        for c in columns:
            sort_func = columns[c][0]
            magic_nine_table.heading(c, command=lambda _col=c: sort_func(magic_nine_table, _col, False))
        # 将show_details函数绑定到Treeview部件的点击事件上
        magic_nine_table.bind("<<TreeviewSelect>>", self.show_stock_detail)
        # 开始计算神奇九转，按钮功能关闭，显示加载中
        self.view.menu.magic_nine_button.configure(state='disabled')
        self.view.menu.magic_nine_button.configure(text=MAGIC_NINE_BTN_DISABLED)
        t = threading.Thread(target=self.init_table, args=())
        t.start()
        
    def init_table(self) -> None:
        magic_stocks = self.model.magic_nine_model.init_table()
        for stock in magic_stocks:
            self.frame.table.insert('', 'end', values = stock)
        self.view.menu.magic_nine_button.configure(state='normal')
        self.view.menu.magic_nine_button.configure(text=MAGIC_NINE_BTN)

