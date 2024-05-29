import customtkinter
from config import APP_NAME, APP_WIDTH, APP_HEIGHT, APP_MIN_WIDTH, APP_MIN_HEIGHT
from .magic_nine_view import MagicNineView

from typing import TypedDict

# a Dict class to help store all kinds of views
class Frames(TypedDict):
    magic_nine: MagicNineView

class View(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry(f'{APP_WIDTH}x{APP_HEIGHT}')
        self.minsize(width=APP_MIN_WIDTH, height=APP_MIN_HEIGHT)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # this frames contains all views for the app
        self.frames: Frames = {}  # type: ignore
        self._add_frame(MagicNineView, "magic_nine")

    def start_mainloop(self) -> None:
        self.mainloop()

    def _add_frame(self, Frame, name: str) -> None:
        # create a Frame instance
        self.frames[name] = Frame(self)
        # add 
        self.frames[name].grid(row=0, column=0, sticky="nsew")