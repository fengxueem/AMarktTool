from config import MAGIC_NINE_FRAME
from models import Model
from views import View

class MagicNineController:
    
    def __init__(self, view : View, model : Model) -> None:
        self.view = view
        self.model = model
        self.frame = self.view.frames[MAGIC_NINE_FRAME]
        
    def init_table(self) -> None:
        magic_stocks = self.model.magic_nine_model.init_table()
        for stock in magic_stocks:
            self.frame.table.insert('', 'end', values = stock)  
