import akshare as ak
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

class StockDetailModel:
    def __init__(self, key : str) -> None:
        self.key = key
        self.stock_code = self._extract_stock_code()
    
    def _extract_stock_code(self):
        return self.key[-6:]
    
    def get_stock_quotes(self, start_date, end_date):
        # 使用akshare获取股票数据
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=self.stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")

        # 准备数据格式
        stock_zh_a_hist_df['日期'] = pd.to_datetime(stock_zh_a_hist_df['日期'])
        stock_zh_a_hist_df['日期'] = mdates.date2num(np.array(stock_zh_a_hist_df['日期'].dt.to_pydatetime()))
        return stock_zh_a_hist_df[['日期', '开盘', '最高', '最低', '收盘']].values