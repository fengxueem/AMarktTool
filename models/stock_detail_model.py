import akshare as ak
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

class StockDetailModel:
    def __init__(self, key : str) -> None:
        self.key = key
        self.stock_code = self._extract_stock_code()
        self.stock_name = self._get_stock_name()
        # quotes 记录每一个交易日的股票数据，其中数据存放顺序如下
        # '日期', '开盘', '最高', '最低', '收盘'
        self.quotes = []
    
    # 从 key 中提取股票代码
    def _extract_stock_code(self):
        return self.key[-6:]
    
    # 从 stock_code 中提取股票名称
    def _get_stock_name(self):
        stock_name = None
        # 上海股票代码以'6'开头
        if self.stock_code.startswith('6'):
            stock_info_df = ak.stock_info_sh_name_code()
            stock_name = stock_info_df.loc[stock_info_df['证券代码'] == self.stock_code, '证券简称'].values[0]
        else:
            stock_info_df = ak.stock_info_sz_name_code()
            stock_name = stock_info_df.loc[stock_info_df['A股代码'] == self.stock_code, 'A股简称'].values[0]
        return stock_name
    
    def get_stock_code(self) -> str: 
        return self.stock_code
    
    def get_stock_name(self) -> str:
        return self.stock_name
    
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
    
    # 根据 quotes 的收盘价计算神奇九转发生的日期与当日最高价
    def get_M9s(self):
        if len(self.quotes) == 0:
            return None
        res = []
        # 计算神奇九转
        for i in range(8, len(self.quotes)):
            # 检查连续9个交易日的收盘价是否都低于它们之前第4天的收盘价
            if all(self.quotes[j][4] < self.quotes[j - 4][4] for j in range(i-8, i+1)):
                res.append((self.quotes[i][0], self.quotes[i][2]))
        return res