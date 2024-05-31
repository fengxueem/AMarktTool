from config import MAGIC_NINE_FRAME, TABLE_STOCK_CODE, TABLE_STOCK_NAME

from views import View
from models import Model

class MagicNineController:
    def __init__(self, view : View, model : Model) -> None:
        self.view = view
        self.model = model
        self.frame = self.view.frames[MAGIC_NINE_FRAME]
        self.all_stocks = model.magic_nine_model.all_stocks
            
    def init_table(self)->None:
        for index, stock in enumerate(self.all_stocks):
            values = (index + 1, stock[TABLE_STOCK_CODE], stock[TABLE_STOCK_NAME])
            self.frame.table.insert('', 'end', values = values)
        