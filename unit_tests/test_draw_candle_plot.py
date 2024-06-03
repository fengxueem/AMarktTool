import customtkinter as ctk
import akshare as ak
import pandas as pd
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# 设置茅台股票代码
stock_code = "600519"
# 储存 K 线图数据
quotes = []
# 创建 customtkinter 窗口
app = ctk.CTk()
app.geometry("1000x800")
app.title("股价查询工具")

# 创建日期输入控件和刷新按钮
start_date_label = ctk.CTkLabel(app, text="开始日期:")
start_date_label.pack(pady=10)
start_date_entry = ctk.CTkEntry(app, placeholder_text="YYYY-MM-DD")
start_date_entry.pack(pady=10)

end_date_label = ctk.CTkLabel(app, text="结束日期:")
end_date_label.pack(pady=10)
end_date_entry = ctk.CTkEntry(app, placeholder_text="YYYY-MM-DD")
end_date_entry.pack(pady=10)

# 创建 matplotlib 图表
fig = Figure()
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=app)
canvas_widget = canvas.get_tk_widget()
# 添加 matplotlib 导航工具栏
toolbar = NavigationToolbar2Tk(canvas, app)
toolbar.update()
# 将图表和工具栏放置到窗口中
canvas_widget.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)
canvas._tkcanvas.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)
# 创建注释文本，初始时不可见
annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

# 更新注释文本的内容和位置
def update_annot(ohlc, x, y):
    date = mdates.num2date(ohlc[0]).strftime('%Y-%m-%d')
    text = f"date: {date}\nopen: {ohlc[1]}\nclose: {ohlc[2]}\nhigh: {ohlc[3]}\nlow: {ohlc[4]}"
    annot.xy = (x, y)
    annot.set_text(text)
    annot.get_bbox_patch().set_alpha(0.4)
    annot.set_visible(True)
    canvas.draw_idle()

# 鼠标悬停事件处理函数
def hover(event):
    vis = annot.get_visible()
    if event.inaxes == ax:
        for i, bar in enumerate(quotes):
            if bar[0] - 0.3 <= event.xdata <= bar[0] + 0.3:
                update_annot(bar, event.xdata, event.ydata)
                return
    if vis:
        annot.set_visible(False)
        canvas.draw_idle()

# 查找指定时间范围内的最大和最小股价
def find_price_range(quotes, start_time, end_time):
    # 筛选出在指定时间范围内的股价数据
    visible_quotes = [q for q in quotes if start_time <= q[0] <= end_time]
    # 初始化最高价和最低价
    high_max = -np.inf
    low_min = np.inf
    # 遍历筛选出的数据，更新最高价和最低价
    for q in visible_quotes:
        high_max = max(high_max, q[2])
        low_min = min(low_min, q[3])
    return low_min, high_max

# 缩放事件处理函数
def zoom(event):
    base_scale = 1.1
    if event.button == 'up' or event.button == 'down':
        if event.key == 'control':
            # 按下 Ctrl 键则代表放大或缩小
            cur_xlim = ax.get_xlim()
            cur_xrange = max(1.0, (cur_xlim[1] - cur_xlim[0]) * 0.5)
            xdata = event.xdata
            if event.button == 'up':
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                scale_factor = base_scale
            # 计算移动步长
            step = cur_xrange * scale_factor
            # 保证移动后不超过股价日期的上下界限
            new_low = max(xdata - step, quotes[0][0])
            new_high = min(xdata + step, quotes[-1][0])
            # 如果缩放到达边界，即某一侧到极限不能再放大或缩小，则另一侧需要弥补放大或缩小的损失。
            if new_low == quotes[0][0]:
                if event.button == 'up':
                    new_high = cur_xlim[1] - step
                elif event.button == 'down':
                    new_high = cur_xlim[1] + step
                # 同样确保其不超过 quotes 范围
                new_high = min(new_high, quotes[-1][0])
            if new_high == quotes[-1][0]:
                if event.button == 'up':
                    new_low = cur_xlim[0] + step
                elif event.button == 'down':
                    new_low = cur_xlim[0] - step
                # 同样确保其不超过 quotes 范围
                new_low = max(new_low, quotes[0][0])
            # 这是新的x轴范围
            new_xlim = [new_low, new_high]
            ax.set_xlim(new_xlim)

            # 根据新的x轴范围计算y轴的最大最小值
            low_min, high_max = find_price_range(quotes, new_xlim[0], new_xlim[1])
            ax.set_ylim([low_min, high_max])
        else: 
            # 平移操作
            cur_xlim = ax.get_xlim()
            # 平移到达左右两边后不能继续平移
            if event.button == 'up' and cur_xlim[1] == quotes[-1][0]:
                return
            if event.button == 'down' and cur_xlim[0] == quotes[0][0]:
                return
            cur_xrange = max(1.0, (cur_xlim[1] - cur_xlim[0]) * 0.02)
            # 计算移动步长
            if event.button == 'up':
                scale_factor = base_scale
            elif event.button == 'down':
                scale_factor = -base_scale
            step = cur_xrange * scale_factor
            # 保证平移后不超过股价日期的上下界限
            new_low = max(cur_xlim[0] + step, quotes[0][0])
            new_high = min(cur_xlim[1] + step, quotes[-1][0])
            # 这是新的x轴范围
            new_xlim = [new_low, new_high]
            ax.set_xlim(new_xlim)

            # 根据新的x轴范围计算y轴的最大最小值
            low_min, high_max = find_price_range(quotes, new_xlim[0], new_xlim[1])
            ax.set_ylim([low_min, high_max])
            
        canvas.draw_idle()

# 连接事件处理函数
canvas.mpl_connect("motion_notify_event", hover)
canvas.mpl_connect('scroll_event', zoom)

# 刷新数据并重新绘制图表的函数
def refresh_data():
    # 因为刷新数据会对 quotes 和 annot 赋值，内部作用域想修改外部作用域必须用 global 申明
    global quotes
    global annot
    # 获取输入的日期，如果为空则设置默认值
    start_date = start_date_entry.get()
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y%m%d')

    end_date = end_date_entry.get()
    if not end_date:
        end_date = datetime.now().strftime('%Y%m%d')
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y%m%d')

    # 使用akshare获取股票数据
    stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date=start_date, end_date=end_date, adjust="qfq")

    # 准备数据格式
    stock_zh_a_hist_df['日期'] = pd.to_datetime(stock_zh_a_hist_df['日期'])
    stock_zh_a_hist_df['日期'] = mdates.date2num(np.array(stock_zh_a_hist_df['日期'].dt.to_pydatetime()))
    quotes = stock_zh_a_hist_df[['日期', '开盘', '最高', '最低', '收盘']].values

    # 清除旧的图表
    ax.clear()

    # 绘制新的 K 线图
    candlestick_ohlc(ax, quotes, width=0.6, colorup='g', colordown='r', alpha=0.8)
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.grid(True)

    # 重绘图表
    canvas.draw_idle()
    # 重绘注释文本
    annot = ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

refresh_button = ctk.CTkButton(app, text="刷新", command=refresh_data)
refresh_button.pack(pady=20)

# 运行应用
app.mainloop()
