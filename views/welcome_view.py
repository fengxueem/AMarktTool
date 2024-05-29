from customtkinter import CTkFrame, CTkLabel, CTkFont

from config import WELCOME_MSG

class WelcomeView(CTkFrame):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)

        self.textbox = CTkLabel(master=self, text=WELCOME_MSG, font=CTkFont(size=40))
        self.textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")