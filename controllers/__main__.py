from config import WELCOME_FRAME
from views import View
from models import Model
from .menu_controller import MenuController

class Controller:
    def __init__(self, view: View, model: Model):
        self.view = view
        self.model = model
        self.menu_controller = MenuController(view, model)

    def start_app(self) -> None:
        # always start the app with the welcome page
        self.view.switch_frame(WELCOME_FRAME)
        self.view.start_mainloop()