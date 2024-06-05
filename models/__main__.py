from config import STOCK_DETAIL_WINDOW
from .k_training_model import KTrainingModel
from .magic_nine_model import MagicNineModel
from .stock_detail_model import StockDetailModel

class Model:
    def __init__(self):
        # this models contains all models for the app
        self.models = {}
        self.magic_nine_model = MagicNineModel()
        self.k_training_model = KTrainingModel()
        
    def add_model(self, model_type: str, name: str) -> None:
        # convert type string to a real class
        ModelClazz = None
        if model_type == STOCK_DETAIL_WINDOW:
            ModelClazz = StockDetailModel
        
        model_key = model_type + name
        if model_key not in self.models:
            # create a Window instance if not existed
            self.models[model_key] = ModelClazz(model_key)
