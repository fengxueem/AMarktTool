from customtkinter import CTkFrame, CTkButton

from config import MAGIC_NINE_BTN

class Menu(CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.magic_nine_button = CTkButton(self, text=MAGIC_NINE_BTN)
        self.magic_nine_button.grid(row=0, column=0, padx=10, pady=5, sticky='nw')
