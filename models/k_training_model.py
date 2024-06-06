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
        # 剩余的k线根数，开局总是 150
        self.kandle_left = 150
        # 钱包余额，开局总是 10k
        self.money_left = 10000
        # 钱包余额，开局总是 10k
        self.last_money_left = 10000
        # 股份余额，开局总是 0 股
        self.stock_left = 0
        # 成本价，开局总是 None
        self.cost_price = None
        # 仓位，开局总是 0%
        self.position = 0.0
        # 本局利润比例，开局总是0%
        self.total_profit = 0.0
        # 当前持仓利润比例，开局总是0%
        self.open_profit = 0.0
        # 随机挑选一只股票用于之后的k线训练
        self.this_stock_to_play, self.start_date, self.end_date, self.quotes, self.start_training_date = self.random_pick_a_stock()
        # 记录当前的训练日期
        self.current_training_date = self.start_training_date
        self.current_training_index = -self.kandle_left - 1
        

    # 获取沪深两个市场的股票代码，不包含 ST 垃圾股票
    def get_all_stock_no_trash_ST(self):
        shanghai_stock_df = ak.stock_info_sh_name_code()
        shanghai_stock_df = shanghai_stock_df[~shanghai_stock_df["证券简称"].str.contains("ST")]
        # 创建一个新的列表，只保留原先需要的属性
        new_shanghai_stock = [{"代码": item[0], "名称": item[1], "上市日期": item[3]} for item in shanghai_stock_df.values]

        # 获取深 A 股实时行情数据
        shenzhen_stock_df = ak.stock_info_sz_name_code()
        shenzhen_stock_df = shenzhen_stock_df[~shenzhen_stock_df["A股简称"].str.contains("ST")]
        new_shenzhen_stock = [{"代码": item[1], "名称": item[2], "上市日期": item[3]} for item in shenzhen_stock_df.values]

        # 合并两个市场的股票
        return new_shanghai_stock + new_shenzhen_stock
    
    def random_pick_a_stock(self):
        this_stock = random.choice(self.all_stocks)
        end_date, start_date = self.get_random_time()
        listing_date = pd.to_datetime(this_stock['上市日期'])
        # 查询上市日期是否在随机生成的开始日期前
        # 保证我们有足够天数的训练样本
        while listing_date > start_date:
            this_stock = random.choice(self.all_stocks)
            end_date, start_date = self.get_random_time()
            listing_date = pd.to_datetime(this_stock['上市日期'])
        quotes = self.get_stock_quotes(this_stock['代码'], start_date, end_date)
        start_training_date = quotes[-self.kandle_left - 1][0]
        return this_stock, start_date, end_date, quotes, start_training_date
    
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

    def go_to_next_day(self):
        self.current_training_index += 1
        self.current_training_date = self.quotes[self.current_training_index][0]
        self.kandle_left -= 1
        self.calculate_profit()
        
    def calculate_profit(self):
        this_closing_price = self.quotes[self.current_training_index][4]
        self.total_profit = (self.money_left + this_closing_price * self.stock_left) / self.last_money_left - 1.0
        if self.cost_price is not None:
            # 持股情况下，用当前收盘价更新新一天的账面利润
            self.open_profit = this_closing_price * 1.0 / self.cost_price - 1.0
        else:
            # 不持股则开盘利润回归 0
            self.open_profit = 0.0
    
    def is_end(self):
        return self.kandle_left == 0
    
    def calculate_position(self):
        if self.cost_price is None:
            self.position = 0.0
            return
        stock = self.cost_price * self.stock_left
        self.position = 1.0 * stock / (stock + self.money_left)
        if self.position > 1.0:
            self.position = 1.0
        
    def get_money_left_str(self):
        # 不保留小数
        return f"{self.money_left:.0f}"
    
    def get_kandle_left_str(self):
        return f"{self.kandle_left}"
    
    def get_position_str(self):
        return f"{self.position * 100:.1f}%"

    def get_open_profit_str(self):
        return f"{self.open_profit * 100:.1f}%"

    def get_total_profit_str(self):
        return f"{self.total_profit * 100:.1f}%"
    
    def settel(self):
        # 如果还有股票在手里则强制以最后一天收盘价卖出
        if self.stock_left > 0:
            self.money_left += self.quotes[-1][4] * self.stock_left
        # 恢复默认值等待下一局开始
        self.kandle_left = 0
        self.stock_left = 0
        self.cost_price = None
        self.position = 0.0
        self.total_profit = 0.0
        self.open_profit = 0.0
        self.last_money_left = self.money_left

    def sell(self, portion):
        # 没有持股，无法卖出
        if self.stock_left <= 0:
            return
        stock_to_sell = self.stock_left * portion
        self.stock_left -= stock_to_sell
        if self.stock_left <= 0:
            self.cost_price = None
            self.stock_left = 0.0
        # 以当日收盘价交易
        self.money_left += self.quotes[self.current_training_index][4] * stock_to_sell
        self.calculate_position()
    
    def buy(self, portion):
        # 钱包没有余额，无法买入
        if self.money_left <= 0:
            return
        money_to_buy = self.money_left * portion
        self.money_left -= money_to_buy
        if self.money_left < 0:
            self.money_left = 0.0
        # 以当日收盘价交易
        stock_to_buy = 1.0 * money_to_buy / self.quotes[self.current_training_index][4]
        # 更新成本价
        if self.cost_price is None:
            self.cost_price = self.quotes[self.current_training_index][4]
        else:
            self.cost_price = (money_to_buy + self.cost_price * self.stock_left) / (stock_to_buy + self.stock_left)
        self.stock_left += stock_to_buy
        self.calculate_position()
        