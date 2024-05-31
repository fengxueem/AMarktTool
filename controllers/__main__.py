from config import WELCOME_FRAME
from models import Model
from .magic_nine_controller import MagicNineController
from .menu_controller import MenuController
from views import View

class Controller:
    def __init__(self, view: View, model: Model):
        self.view = view
        self.model = model
        self.magic_nine_controller = MagicNineController(view, model)
        self.menu_controller = MenuController(view, model, self.magic_nine_controller)

    def start_app(self) -> None:
        # always start the app with the welcome page
        self.view.switch_frame(WELCOME_FRAME)
        self.view.start_mainloop()