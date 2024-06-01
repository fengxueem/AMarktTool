from config import APP_NAME, APP_WIDTH, APP_HEIGHT, APP_MIN_WIDTH, APP_MIN_HEIGHT, MAGIC_NINE_FRAME, WELCOME_FRAME
from config import STOCK_DETAIL_WINDOW
from .magic_nine_view import MagicNineView
from .menu_view import Menu
from .welcome_view import WelcomeView
from .stock_detail_window import StockDetailWindow

import customtkinter
from typing import TypedDict

# a Dict class to help store all kinds of views
class Frames(TypedDict):
    magic_nine: MagicNineView
    welcome: WelcomeView

class View(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry(f'{APP_WIDTH}x{APP_HEIGHT}')
        self.minsize(width=APP_MIN_WIDTH, height=APP_MIN_HEIGHT)
        self.grid_columnconfigure(0, weight=1)
        # row 0 is for menu
        self.grid_rowconfigure(0, weight=1)
        # row 1 if for other frames
        self.grid_rowconfigure(1, weight=100)
        # create menu
        self._add_menu()
        # this frames contains all views for the app
        self.frames: Frames = {}  # type: ignore
        self._add_frame(MagicNineView, MAGIC_NINE_FRAME)
        self._add_frame(WelcomeView, WELCOME_FRAME)
        # this windows contains all windows for the app
        self.windows = {}

    def start_mainloop(self) -> None:
        self.mainloop()

    def _add_menu(self)->None:
        self.menu = Menu(self)
        self.menu.grid(row=0, column=0, sticky="new")
    
    def _add_frame(self, Frame, name: str) -> None:
        # create a Frame instance
        self.frames[name] = Frame(self)
        # add 
        self.frames[name].grid(row=1, column=0, sticky="nsew")

    def add_window(self, window_type: str, name: str) -> None:
        # convert type string to a real class
        WindowClazz = None
        if window_type == STOCK_DETAIL_WINDOW:
            WindowClazz = StockDetailWindow
        
        windows_key = window_type + name
        if windows_key in self.windows:
            # focus a Window if already existed
            self.windows[windows_key].deiconify()
            self.windows[windows_key].focus()
        else:
            # create a Window instance if not existed
            self.windows[windows_key] = WindowClazz(self)
    
    def hide_window(self, key: str) -> None:
        if key in self.windows:
            self.windows[key].withdraw()
        
    def switch_frame(self, name: str) -> None:
        frame = self.frames[name]
        frame.tkraise()
