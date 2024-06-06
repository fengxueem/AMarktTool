import akshare as ak
from datetime import datetime, timedelta
import random
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

class KTrainingModel:
    
    def __init__(self) -> None:
        # 获取沪 A 股实时行情数据
        # 不要垃圾 ST 股票！！！
        self.all_stocks = self.get_all_stock_no_trash_ST()
        # 随机挑选一只股票用于之后的k线训练
        self.this_stock_to_play, self.start_date, self.end_date, self.quotes, self.start_training_date = self.random_pick_a_stock()

    # 获取沪深两个市场的股票代码，不包含 ST 垃圾股票
    def get_all_stock_no_trash_ST(self):
        shanghai_stock_df = ak.stock_sh_a_spot_em()
        shanghai_stock_df = shanghai_stock_df[~shanghai_stock_df["名称"].str.contains("ST")]
        # 创建一个新的列表，只保留原先需要的属性
        new_shanghai_stock = [{"序号": item[0], "代码": item[1], "名称": item[2]} for item in shanghai_stock_df.values]

        # 获取深 A 股实时行情数据
        shenzhen_stock_df = ak.stock_sz_a_spot_em()
        shenzhen_stock_df = shenzhen_stock_df[~shenzhen_stock_df["名称"].str.contains("ST")]
        new_shenzhen_stock = [{"序号": item[0], "代码": item[1], "名称": item[2]} for item in shenzhen_stock_df.values]

        # 合并两个市场的股票
        return new_shanghai_stock + new_shenzhen_stock
    
    def random_pick_a_stock(self):
        this_stock = random.choice(self.all_stocks)
        end_date, start_date = self.get_random_time()
        listing_date = self.get_stock_listing_date(this_stock['代码'])
        # 查询上市日期是否在随机生成的开始日期前
        # 保证我们有足够天数的训练样本
        while listing_date > start_date:
            this_stock = random.choice(self.all_stocks)
            end_date, start_date = self.get_random_time()
            listing_date = self.get_stock_listing_date(this_stock['代码'])
        quotes = self.get_stock_quotes(this_stock['代码'], start_date, end_date)
        start_training_date = quotes[-150][0]
        return this_stock, start_date, end_date, quotes, start_training_date
        
    def get_stock_listing_date(self, stock_code):
        listing_date = None
        # 上海股票代码以'6'开头
        if stock_code.startswith('6'):
            stock_info_df = ak.stock_info_sh_name_code()
            listing_date = stock_info_df.loc[stock_info_df['证券代码'] == stock_code, '上市日期'].values[0]
        else:
            stock_info_df = ak.stock_info_sz_name_code()
            listing_date = stock_info_df.loc[stock_info_df['A股代码'] == stock_code, 'A股上市日期'].values[0]
        return pd.to_datetime(listing_date)     
    
    # 使用akshare获取股票数据
    def get_stock_quotes(self, stock_code, start_date, end_date):
        stock_zh_a_hist_df = ak.stock_zh_a_hist(
            symbol=stock_code,
            period="daily",
            start_date=start_date.strftime('%Y%m%d'),
            end_date=end_date.strftime('%Y%m%d'),
            adjust="qfq"
            )

        # 准备数据格式
        stock_zh_a_hist_df['日期'] = pd.to_datetime(stock_zh_a_hist_df['日期'])
        stock_zh_a_hist_df['日期'] = mdates.date2num(np.array(stock_zh_a_hist_df['日期'].dt.to_pydatetime()))
        return stock_zh_a_hist_df[['日期', '开盘', '最高', '最低', '收盘']].values

    # 随机生成一对至少间隔24个月的时间对
    def get_random_time(self):
        # 获取当前日期
        current_date = datetime.now()
        # 随机生成结束日期（在过去10天内）
        end_date = current_date - timedelta(days=random.randint(0, 10))  # 10到60天之间的随机天数
        # 随机生成开始日期（在end_date之前24个月外）
        start_date = end_date - timedelta(days=random.randint(730, 800))  # 730到1095天之间的随机天数
        return end_date, start_date
    
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