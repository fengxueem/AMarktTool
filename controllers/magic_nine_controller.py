import akshare as ak
from datetime import datetime, timedelta

from config import MAGIC_NINE_FRAME, TABLE_STOCK_CODE, TABLE_STOCK_NAME

from views import View
from models import Model

class MagicNineController:
    def __init__(self, view : View, model : Model) -> None:
        self.view = view
        self.model = model
        self.frame = self.view.frames[MAGIC_NINE_FRAME]
        self.all_stocks = model.magic_nine_model.all_stocks
    
    @staticmethod
    def bigger_than_4_days_later(dataframe_from_ak, row):
        if dataframe_from_ak.loc[row, '收盘'] > dataframe_from_ak.loc[row + 4, '收盘']:
            return True
        else:
            return False
    
    # 检查布尔数组中是否存在连续的 magic_number 个 True 值
    # 如有，则返回最后一次出现的下标位置
    # 如没有，则返回-1
    @staticmethod
    def find_magic_number(bool_array, magic_number):
        sum_array = [0] * len(bool_array)
        # 初始化变量来记录连续True的起始下标
        last_index = -1
        count = 0  # 连续True的计数器

        # 遍历布尔数组
        for index, current in enumerate(bool_array):
            if current:
                # 当我们找到第一个 True 时，增加计数器
                count += 1
                sum_array[index] = count
            else:
                # 如果遇到False，重置计数器
                count = 0
        # 倒序遍历数组
        for i in range(len(sum_array) - 1, -1, -1):
            if sum_array[i] > magic_number:
                return i  # 返回找到的下标
        return -1  # 如果没有找到，则返回-1


    def init_table(self) -> None:
        # 获取今天的日期和时间
        today = datetime.now()
        today_str = today.strftime("%Y%m%d")
        # # 计算约一个月前的日期
        one_month_ago = (today - timedelta(days=28))
        one_month_ago_str = one_month_ago.strftime("%Y%m%d")
        valid_magic_count = 0
        for _, stock in enumerate(self.all_stocks):
            # 查询这只股票的往日价格
            stock_zh_a_hist_df = ak.stock_zh_a_hist(
                symbol=stock[TABLE_STOCK_CODE],
                period="daily",
                start_date=one_month_ago_str,
                end_date=today_str,
                adjust="hfq"
                )
            # 生成一个每日价格是否超过当日后第4天的布尔数组，用于判断神奇 X 转
            daily_result = []
            for entry in range(0, stock_zh_a_hist_df.shape[0] - 4):
                daily_result.append(
                    self.bigger_than_4_days_later(
                        dataframe_from_ak = stock_zh_a_hist_df,
                        row = entry
                        )
                    )
            # 查询神奇 X 转是否存在
            magic_turn_index = self.find_magic_number(daily_result, 9)
            # 如果存在则将其放入数据表格中
            if magic_turn_index > -1:
                valid_magic_count += 1
                signal_date = stock_zh_a_hist_df.loc[magic_turn_index, '日期']
                values = (valid_magic_count, stock[TABLE_STOCK_CODE], stock[TABLE_STOCK_NAME], signal_date)
                self.frame.table.insert('', 'end', values = values)
        