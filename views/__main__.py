import customtkinter

class View(customtkinter.CTk):
    def __init__(self):
        super().__init__()

    def start_mainloop(self) -> None:
        self.mainloop()