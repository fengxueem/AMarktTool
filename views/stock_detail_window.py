from customtkinter import CTkToplevel

class StockDetailWindow(CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        
        self.geometry("400x200")

