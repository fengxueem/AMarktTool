from views import View

class Controller:
    def __init__(self, view: View):
        self.view = view

    def start_app(self) -> None:
        self.view.start_mainloop()