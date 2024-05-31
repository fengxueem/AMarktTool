from config import MAGIC_NINE_FRAME
from models import Model
from views import View


class MenuController:
    def __init__(self, view : View, model : Model) -> None:
        self.view = view
        self.model = model
        self.frame = self.view.menu
        
        self._bind()
        
    def _bind(self):
        self.frame.magic_nine_button.configure(command = self.magic_nine_btn)
    
    def magic_nine_btn(self) -> None:
        self.view.switch_frame(MAGIC_NINE_FRAME)
