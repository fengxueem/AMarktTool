from .__base__ import BaseController
from .stock_detail_controller import StockDetailController
from models import Model
from views import View


class StockDetailWindowController(BaseController):
    def __init__(self, view : View, model : Model, key : str) -> None:
        self.view = view
        self.model = model
        self.key = key
        self.window = self.view.windows[key]
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.stock_detail_controller = StockDetailController(self.window, model)
        self.stock_detail_controller.mediator = self
    
    def on_closing(self):
        self.mediator.notify(self, "HIDE_STOCK_DETAIL_WINDOWS", self.key)