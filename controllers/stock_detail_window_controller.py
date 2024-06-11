from .__base__ import BaseController
from .stock_detail_controller import StockDetailController
from config import EVENT_HIDE_STOCK_DETAIL
from models import Model
from views import View

class StockDetailWindowController(BaseController):
    def __init__(self, view : View, model : Model, key : str) -> None:
        self.key = key
        # 从 View 类管家中获取当前窗口的实际控制 view 与 model
        self.view = view.windows[key]
        self.view.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.model = model.models[key]
        self.stock_detail_controller = StockDetailController(self.view, self.model)
        self.stock_detail_controller.mediator = self
    
    def on_closing(self):
        self.mediator.notify(self, EVENT_HIDE_STOCK_DETAIL, (self.key))