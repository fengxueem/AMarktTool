from customtkinter import CTkFrame, CTkLabel

class MagicNineView(CTkFrame):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

        self.header = CTkLabel(self, text="TEST")
        self.header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")