class StockDetailModel:
    def __init__(self, key : str) -> None:
        self.key = key
        self.stock_code = self._extract_stock_code()
    
    def _extract_stock_code(self):
        return self.key[-6:]