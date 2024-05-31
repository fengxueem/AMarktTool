from config import MAGIC_NINE_FRAME
from config import MAGIC_NINE_BTN, MAGIC_NINE_BTN_DISABLED
from config import TABLE_INDEX, TABLE_STOCK_CODE, TABLE_SIGNAL_DATE
from models import Model
from views import View

import threading

class MagicNineController:
    
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
        for c in columns:
            sort_func = columns[c][0]
            self.frame.table.heading(c, command=lambda _col=c: sort_func(self.frame.table, _col, False))      
        # start calculating magic nine as soon as the app started
        t = threading.Thread(target=self.init_table, args=())
        t.start()
        
    def init_table(self) -> None:
        self.view.menu.magic_nine_button.configure(state='disabled')
        self.view.menu.magic_nine_button.configure(text=MAGIC_NINE_BTN_DISABLED)
        magic_stocks = self.model.magic_nine_model.init_table()
        for stock in magic_stocks:
            self.frame.table.insert('', 'end', values = stock)
        self.view.menu.magic_nine_button.configure(state='normal')
        self.view.menu.magic_nine_button.configure(text=MAGIC_NINE_BTN)
        
