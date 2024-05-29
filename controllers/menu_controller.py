from config import MAGIC_NINE_FRAME

from views import View
from models import Model
from .magic_nine_controller import MagicNineController

class MenuController:
    def __init__(self, view : View, model : Model, magic_nine_controller: MagicNineController) -> None:
        self.view = view
        self.model = model
        self.magic_nine_controller = magic_nine_controller
        self.frame = self.view.menu
        
        self._bind()
        
    def _bind(self):
        self.frame.magic_nine_button.configure(command = self.magic_nine_btn)
    
    def magic_nine_btn(self) -> None:
        self.magic_nine_controller.init_table()
        self.view.switch_frame(MAGIC_NINE_FRAME)