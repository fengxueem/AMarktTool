from .__base__ import Mediator
from config import WELCOME_FRAME
from config import STOCK_DETAIL_WINDOW, STOCK_DETAIL_CONTROLLER, STOCK_DETAIL_MODEL
from config import EVENT_OPEN_STOCK_DETAIL, EVENT_HIDE_STOCK_DETAIL
from models import Model
from .k_training_controller import KTrainingController
from .magic_nine_controller import MagicNineController
from .menu_controller import MenuController
from .stock_detail_window_controller import StockDetailWindowController
from views import View

class Controller(Mediator):
    """
    各个 controller 之间的实际中介者
    """
    def __init__(self, view: View, model: Model):
        self.view = view
        self.model = model
        self.magic_nine_controller = MagicNineController(view, model)
        self.magic_nine_controller.mediator = self
        self.menu_controller = MenuController(view, model)
        self.menu_controller.mediator = self
        self.k_training_controller = KTrainingController(view, model)
        self.k_training_controller.mediator = self
        # this contains all windows controller for the app
        self.window_controllers = {}

    def start_app(self) -> None:
        # always start the app with the welcome page
        self.view.switch_frame(WELCOME_FRAME)
        self.view.start_mainloop()
    
    def notify(self, sender: object, event: str, *msg) -> None:
        if sender is self.magic_nine_controller and event == EVENT_OPEN_STOCK_DETAIL:
            self.view.add_window(STOCK_DETAIL_WINDOW, msg)
            self.model.add_model(STOCK_DETAIL_MODEL, msg)
            self.add_windows_controller(STOCK_DETAIL_CONTROLLER, msg)
        elif event == EVENT_HIDE_STOCK_DETAIL:
            self.view.hide_window(msg)

    def add_windows_controller(self, type: str, msg) -> None:
        # convert type string to class type
        WindowControllerClass = None
        if type == STOCK_DETAIL_CONTROLLER:
            WindowControllerClass = StockDetailWindowController
        
        key, _ = msg[0]
        controller_key = type + key
        if controller_key not in self.window_controllers:       
            # create a controller instance if not existed
            self.window_controllers[controller_key] = WindowControllerClass(self.view, self.model, controller_key)
            self.window_controllers[controller_key].mediator = self
