from config import TABLE_STOCK_CODE, TABLE_STOCK_NAME
from config import AK_DATE_FORMAT, AK_DATAFRAME_DATE, AK_DATAFRAME_CLOSING_PRICE

import akshare as ak
from datetime import datetime, timedelta
from multiprocessing import Pool

class MagicNineModel:
    
    def __init__(self) -> None:
        self.pool = Pool(processes=16)
        # 获取沪深两个市场的股票代码，不包含 ST 垃圾股票
        # 获取沪 A 股实时行情数据
        shanghai_stock_df = ak.stock_sh_a_spot_em()
        shanghai_stock_df = shanghai_stock_df[~shanghai_stock_df["名称"].str.contains("ST")]
        # 创建一个新的列表，只保留原先需要的属性
        new_shanghai_stock = [{"序号": item[0], "代码": item[1], "名称": item[2]} for item in shanghai_stock_df.values]

        # 获取深 A 股实时行情数据
        shenzhen_stock_df = ak.stock_sz_a_spot_em()
        shenzhen_stock_df = shenzhen_stock_df[~shenzhen_stock_df["名称"].str.contains("ST")]
        new_shenzhen_stock = [{"序号": item[0], "代码": item[1], "名称": item[2]} for item in shenzhen_stock_df.values]

        # 合并两个市场的股票
        self.all_stocks = new_shanghai_stock + new_shenzhen_stock
        
    @staticmethod
    def bigger_than_x_days_later(dataframe_from_ak, x, row):
        if dataframe_from_ak.loc[row, AK_DATAFRAME_CLOSING_PRICE] > dataframe_from_ak.loc[row + x, AK_DATAFRAME_CLOSING_PRICE]:
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
            if sum_array[i] >= magic_number:
                return i  # 返回找到的下标
        return -1  # 如果没有找到，则返回-1

    @staticmethod
    def process_stock(stock, start_date_str, end_date_str):
        # 查询这只股票的往日价格
        stock_zh_a_hist_df = ak.stock_zh_a_hist(
            symbol=stock[TABLE_STOCK_CODE],
            period="daily",
            start_date=start_date_str,
            end_date=end_date_str,
            adjust="hfq"
            )
        # 生成一个每日价格是否超过当日后第 magic_number // 2 天的布尔数组，用于判断神奇 X 转
        daily_result = []
        magic_number = 9
        half_magic_num = magic_number // 2
        # 边界条件：比较收盘价高低时，不用考虑最开始的 magic_number // 2 天
        for entry in range(0, stock_zh_a_hist_df.shape[0] - half_magic_num):
            daily_result.append(
                MagicNineModel.bigger_than_x_days_later(
                    dataframe_from_ak = stock_zh_a_hist_df,
                    x = half_magic_num,
                    row = entry
                    )
                )
        # 查询神奇 X 转是否存在
        magic_turn_index = MagicNineModel.find_magic_number(daily_result, magic_number)
        # 如果存在则将其放入数据表格中
        if magic_turn_index > -1:
            # 由于我们在比较数据时，排除了前 magic_number // 2 天，因此这里的下标需要加上 magic_number // 2 天才是信号日期
            signal_date = stock_zh_a_hist_df.loc[magic_turn_index + half_magic_num, AK_DATAFRAME_DATE]
            return (stock[TABLE_STOCK_CODE], stock[TABLE_STOCK_NAME], signal_date)
        return None

    def init_table(self) -> None:
        # 获取今天的日期和时间
        today = datetime.now()
        today_str = today.strftime(AK_DATE_FORMAT)
        # 计算约一个月前的日期
        one_month_ago = (today - timedelta(days=27))
        one_month_ago_str = one_month_ago.strftime(AK_DATE_FORMAT)
        
        valid_magic_list = []
        for _, stock in enumerate(self.all_stocks):
            # 创建并启动进程
            result = self.pool.apply_async(MagicNineModel.process_stock, (stock, one_month_ago_str, today_str))
            valid_magic_list.append(result)

        # 关闭进程池，不添加新的进程
        self.pool.close()
        # 等待所有进程完成
        self.pool.join()
        valid_magic_count = 0
        magic_stocks = []
        # 挑选出所有不是None的有效结果
        for valid_magic_stock in valid_magic_list:
            res = valid_magic_stock.get()
            if res is not None:
                # 为每个结果配上一个ID号
                valid_magic_count += 1
                magic_stocks.append((valid_magic_count,) + res)
        return magic_stocks