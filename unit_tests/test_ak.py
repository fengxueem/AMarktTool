import akshare as ak

# 获取沪深两个市场的股票代码，不包含 ST 垃圾股票
def get_all_active_stock_codes():
     # 获取沪 A 股实时行情数据
    shanghai_stock_df = ak.stock_sh_a_spot_em()
    shanghai_stock_df = shanghai_stock_df[~shanghai_stock_df["名称"].str.contains("ST")]
    shanghai_stock_codes = shanghai_stock_df["代码"].tolist()

    # 获取深 A 股实时行情数据
    shenzhen_stock_df = ak.stock_sz_a_spot_em()
    shenzhen_stock_df = shenzhen_stock_df[~shenzhen_stock_df["名称"].str.contains("ST")]
    shenzhen_stock_codes = shenzhen_stock_df["代码"].tolist()

    # 合并两个市场的股票代码
    all_stock_codes = shanghai_stock_codes + shenzhen_stock_codes

    return all_stock_codes

if __name__ == "__main__":
    all_active_stock_codes = get_all_active_stock_codes()
    print("所有沪深两个市场的股票代码（无 ST 垃圾股）：", all_active_stock_codes)
    print(f"共：{len(all_active_stock_codes)}个")
