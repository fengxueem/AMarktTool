from config import STOCK_DETAIL_WINDOW
from models import Model
from views import View

from .__base__ import BaseController

class StockDetailController(BaseController):
    def __init__(self, view : View, model : Model, key : str) -> None:
        self.view = view
        self.model = model
        self.key = key
        self.window = self.view.windows[key]
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        self.mediator.notify(self, "HIDE_STOCK_DETAIL_WINDOWS", self.key)