import akshare as ak
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

class StockDetailModel:
    def __init__(self, key : str) -> None:
        self.key = key
        self.stock_code = self._extract_stock_code()
        self.quotes = []
    
    # 从 key 中提取股票代码
    def _extract_stock_code(self):
        return self.key[-6:]
    
    # 查找指定时间范围内的最大和最小股价
    def find_price_range(self, start_time, end_time):
        # 筛选出在指定时间范围内的股价数据
        visible_quotes = [q for q in self.quotes if start_time <= q[0] <= end_time]
        # 初始化最高价和最低价
        high_max = -np.inf
        low_min = np.inf
        # 遍历筛选出的数据，更新最高价和最低价
        for q in visible_quotes:
            high_max = max(high_max, q[2])
            low_min = min(low_min, q[3])
        return low_min, high_max
    
    # 使用akshare获取股票数据
    def get_stock_quotes(self, start_date, end_date):
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=self.stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")

        # 准备数据格式
        stock_zh_a_hist_df['日期'] = pd.to_datetime(stock_zh_a_hist_df['日期'])
        stock_zh_a_hist_df['日期'] = mdates.date2num(np.array(stock_zh_a_hist_df['日期'].dt.to_pydatetime()))
        self.quotes = stock_zh_a_hist_df[['日期', '开盘', '最高', '最低', '收盘']].values
        return self.quotes
    
    # 根据 quotes 的收盘价计算 MA 线: MA5，MA10，MA20
    def get_MAs(self):
        if len(self.quotes) == 0:
            return None
        close_prices = self.quotes[:, 4]  # 收盘价位于第五列
        ma5 = pd.Series(close_prices).rolling(window=5).mean()
        ma10 = pd.Series(close_prices).rolling(window=10).mean()
        ma20 = pd.Series(close_prices).rolling(window=20).mean()
        return {"MA5": ma5, "MA10":ma10, "MA20": ma20}