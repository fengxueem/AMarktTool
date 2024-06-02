from config import STOCK_DETAIL_WINDOW_WIDTH, STOCK_DETAIL_WINDOW_HEIGHT
from config import STOCK_DETAIL_FRAME
from customtkinter import CTkToplevel
from .stock_detail_view import StockDetailView

from typing import TypedDict

# a Dict class to help store all kinds of views
class Frames(TypedDict):
    stock_detail: StockDetailView

class StockDetailWindow(CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        
        self.geometry(f"{STOCK_DETAIL_WINDOW_WIDTH}x{STOCK_DETAIL_WINDOW_HEIGHT}")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # this frames contains all views for the app
        self.frames: Frames = {}  # type: ignore
        self._add_frame(StockDetailView, STOCK_DETAIL_FRAME)
        
    def _add_frame(self, Frame, name: str) -> None:
        # create a Frame instance
        self.frames[name] = Frame(self)
        # add 
        self.frames[name].grid(row=0, column=0, sticky="nsew")