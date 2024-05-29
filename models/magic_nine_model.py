import akshare as ak

class MagicNineModel:
    
    def __init__(self) -> None:
        # 获取沪深两个市场的股票代码，不包含 ST 垃圾股票
        # 获取沪 A 股实时行情数据
        shanghai_stock_df = ak.stock_sh_a_spot_em()
        shanghai_stock_df = shanghai_stock_df[~shanghai_stock_df["名称"].str.contains("ST")]
        shanghai_stock_codes = shanghai_stock_df["代码"].tolist()

        # 获取深 A 股实时行情数据
        shenzhen_stock_df = ak.stock_sz_a_spot_em()
        shenzhen_stock_df = shenzhen_stock_df[~shenzhen_stock_df["名称"].str.contains("ST")]
        shenzhen_stock_codes = shenzhen_stock_df["代码"].tolist()

        # 合并两个市场的股票代码
        self.all_stock_codes = shanghai_stock_codes + shenzhen_stock_codes
