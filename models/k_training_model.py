from config import K_TRAINING_DEFAULT_KANDLE_LEFT
from config import K_TRAINING_DEFAULT_MONEY_LEFT
from config import STOCK_DATA_CODE, STOCK_DATA_NAME
from config import STOCK_DATA_LISTING_DATE
from config import AK_API_SH_STOCK_NAME, AK_API_SZ_STOCK_NAME, AK_API_STUPID_ST
from config import AK_API_HIST_DF_DATE, AK_API_HIST_DF_OPEN, AK_API_HIST_DF_CLOSE, AK_API_HIST_DF_HIGH, AK_API_HIST_DF_LOW
from config import K_TRAINING_MA_LINE_5, K_TRAINING_MA_LINE_10, K_TRAINING_MA_LINE_20
from config import K_TRAINING_RECORD_FILE_NAME

import akshare as ak
from datetime import datetime, timedelta
import random
import matplotlib.dates as mdates
import numpy as np
import os
import pandas as pd
import sys
import yaml

class KTrainingModel:
    
    def __init__(self) -> None:
        # 获取沪 A 股实时行情数据
        # 不要垃圾 ST 股票！！！
        self.all_stocks = self.get_all_stock_no_trash_ST()
        # 剩余的k线根数，每一句开局总是 150
        self.kandle_left = K_TRAINING_DEFAULT_KANDLE_LEFT
        # 股份余额，每一句开局总是 0 股
        self.stock_left = 0
        # 成本价，每一句开局总是 None
        self.cost_price = None
        # 仓位，每一句开局总是 0%
        self.position = 0.0
        # 本局利润比例，每一句开局总是0%
        self.total_profit = 0.0
        # 当前持仓利润比例，每一句开局总是0%
        self.open_profit = 0.0
        # 随机挑选一只股票用于之后的k线训练
        self.this_stock_to_play, self.start_date, self.end_date, self.quotes, self.start_training_date_in_float = self.random_pick_a_stock()
        # 记录当前的训练日期
        self.current_training_date_in_float = self.start_training_date_in_float
        self.current_training_index = -self.kandle_left - 1
        # 记录本局的买入卖出日期
        # （买入日期，收盘价）
        self.buy_records = []
        # （卖出日期，收盘价）
        self.sell_records = []
        # 从本地文件中读取历史记录
        self.record_file_path = self.get_current_python_file_path()
        self.read_records_from_yaml()
        
    def restart(self):
        # 恢复默认值
        self.kandle_left = K_TRAINING_DEFAULT_KANDLE_LEFT
        self.stock_left = 0
        self.cost_price = None
        self.position = 0.0
        self.total_profit = 0.0
        self.open_profit = 0.0
        self.last_money_left = self.money_left
        self.buy_records.clear()
        self.sell_records.clear()
        # 随机挑选一只股票用于之后的k线训练
        self.this_stock_to_play, self.start_date, self.end_date, self.quotes, self.start_training_date_in_float = self.random_pick_a_stock()
        # 记录当前的训练日期
        self.current_training_date_in_float = self.start_training_date_in_float
        self.current_training_index = -self.kandle_left - 1

    # 获取沪深两个市场的股票代码，不包含 ST 垃圾股票
    def get_all_stock_no_trash_ST(self):
        shanghai_stock_df = ak.stock_info_sh_name_code()
        shanghai_stock_df = shanghai_stock_df[~shanghai_stock_df[AK_API_SH_STOCK_NAME].str.contains(AK_API_STUPID_ST)]
        # 创建一个新的列表，只保留原先需要的属性
        new_shanghai_stock = [{STOCK_DATA_CODE: item[0], STOCK_DATA_NAME: item[1], STOCK_DATA_LISTING_DATE: item[3]} for item in shanghai_stock_df.values]

        # 获取深 A 股实时行情数据
        shenzhen_stock_df = ak.stock_info_sz_name_code()
        shenzhen_stock_df = shenzhen_stock_df[~shenzhen_stock_df[AK_API_SZ_STOCK_NAME].str.contains(AK_API_STUPID_ST)]
        new_shenzhen_stock = [{STOCK_DATA_CODE: item[1], STOCK_DATA_NAME: item[2], STOCK_DATA_LISTING_DATE: item[3]} for item in shenzhen_stock_df.values]

        # 合并两个市场的股票
        return new_shanghai_stock + new_shenzhen_stock
    
    def random_pick_a_stock(self):
        this_stock = random.choice(self.all_stocks)
        end_date, start_date = self.get_random_time()
        listing_date = pd.to_datetime(this_stock[STOCK_DATA_LISTING_DATE])
        # 查询上市日期是否在随机生成的开始日期前
        # 保证我们有足够天数的训练样本
        while listing_date > start_date:
            this_stock = random.choice(self.all_stocks)
            end_date, start_date = self.get_random_time()
            listing_date = pd.to_datetime(this_stock[STOCK_DATA_LISTING_DATE])
        quotes = self.get_stock_quotes(this_stock[STOCK_DATA_CODE], start_date, end_date)
        start_training_date_in_float = quotes[-self.kandle_left - 1][0]
        return this_stock, start_date, end_date, quotes, start_training_date_in_float
    
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
        stock_zh_a_hist_df[AK_API_HIST_DF_DATE] = pd.to_datetime(stock_zh_a_hist_df[AK_API_HIST_DF_DATE])
        stock_zh_a_hist_df[AK_API_HIST_DF_DATE] = mdates.date2num(np.array(stock_zh_a_hist_df[AK_API_HIST_DF_DATE].dt.to_pydatetime()))
        return stock_zh_a_hist_df[[AK_API_HIST_DF_DATE, AK_API_HIST_DF_OPEN, AK_API_HIST_DF_HIGH, AK_API_HIST_DF_LOW, AK_API_HIST_DF_CLOSE]].values

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
        return {K_TRAINING_MA_LINE_5: ma5, K_TRAINING_MA_LINE_10: ma10, K_TRAINING_MA_LINE_20: ma20}
    
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
        self.current_training_date_in_float = self.quotes[self.current_training_index][0]
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
        res = False
        # 如果还有股票在手里则强制以最后一天收盘价卖出
        if self.stock_left > 0:
            self.money_left += self.quotes[-1][4] * self.stock_left
            self.sell_records.append((self.quotes[-1][0], self.quotes[-1][4]))
            self.cost_price = None
            self.stock_left = 0.0
            self.calculate_profit()
            self.last_money_left = self.money_left
            res = True
        self.save_records_to_yaml()
        return res

    def sell(self, portion):
        # 没有持股，无法卖出
        if self.stock_left <= 0:
            return False
        stock_to_sell = self.stock_left * portion
        self.stock_left -= stock_to_sell
        if self.stock_left <= 0:
            self.cost_price = None
            self.stock_left = 0.0
        # 以当日收盘价交易
        self.money_left += self.quotes[self.current_training_index][4] * stock_to_sell
        self.calculate_position()
        # 记录卖出
        self.sell_records.append((self.quotes[self.current_training_index][0], self.quotes[self.current_training_index][4]))
        return True
    
    def buy(self, portion):
        # 钱包没有余额，无法买入
        if self.money_left <= 0:
            return False
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
        # 记录买入
        self.buy_records.append((self.quotes[self.current_training_index][0], self.quotes[self.current_training_index][4]))
        return True
    
    def get_buy_records(self):
        return self.buy_records

    def get_sell_records(self):
        return self.sell_records
    
    def get_cost_price(self):
        return self.cost_price
    
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
    
    # 查找当前运行的 Python 文件的路径
    def get_current_python_file_path(self):
        # 获取当前模块的完整路径
        current_file_path = os.path.abspath(sys.argv[0])
        dir = os.path.dirname(current_file_path)
        return os.path.join(dir, K_TRAINING_RECORD_FILE_NAME)
    
    # 将训练记录保存到 YAML 文件
    def save_records_to_yaml(self):       
        # 完整的文件路径
        filepath = self.record_file_path
        
        # 将数据写入 YAML 文件
        with open(filepath, 'w') as file:
            yaml.dump(
                {
                    'last_money_left': int(self.last_money_left)
                },
                file)

    # 从 YAML 文件读取之前的训练记录
    def read_records_from_yaml(self):
        # 完整的文件路径
        filepath = self.record_file_path
        
        # 读取 YAML 文件
        # 钱包余额，money_left，每一局开局总是 10k 或上一局结束的余额
        # 上一局钱包余额，last_money_left，若还未开局则默认是 10k
        try:
            with open(filepath, 'r') as file:
                data = yaml.safe_load(file)
            self.last_money_left = data['last_money_left']
            self.money_left = self.last_money_left
        except FileNotFoundError:
            self.money_left = K_TRAINING_DEFAULT_MONEY_LEFT
            self.last_money_left = K_TRAINING_DEFAULT_MONEY_LEFT
