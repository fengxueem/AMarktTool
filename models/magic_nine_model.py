import akshare as ak

class MagicNineModel:
    
    def __init__(self) -> None:
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
