from config import MAGIC_NINE_FRAME
from config import MAGIC_NINE_BTN, MAGIC_NINE_BTN_DISABLED
from models import Model
from views import View

import threading

class MagicNineController:
    
    def __init__(self, view : View, model : Model) -> None:
        self.view = view
        self.model = model
        self.frame = self.view.frames[MAGIC_NINE_FRAME]
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
        
