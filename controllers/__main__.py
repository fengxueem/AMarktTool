from config import WELCOME_FRAME
from views import View
from .menu_controller import MenuController

class Controller:
    def __init__(self, view: View):
        self.view = view
        self.menu_controller = MenuController(view)

    def start_app(self) -> None:
        # always start the app with the welcome page
        self.view.switch_frame(WELCOME_FRAME)
        self.view.start_mainloop()