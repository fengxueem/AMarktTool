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

# 缩放事件处理函数
def zoom(event):
    base_scale = 1.1
    if event.button == 'up' or event.button == 'down':
        if event.key == 'control':  # 检查是否按下 Ctrl 键
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()
            cur_xrange = (cur_xlim[1] - cur_xlim[0]) * 0.5
            cur_yrange = (cur_ylim[1] - cur_ylim[0]) * 0.5
            xdata = event.xdata
            ydata = event.ydata
            if event.button == 'up':
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                scale_factor = base_scale
            else:
                scale_factor = 1
            ax.set_xlim([xdata - cur_xrange * scale_factor,
                         xdata + cur_xrange * scale_factor])
            ax.set_ylim([ydata - cur_yrange * scale_factor,
                         ydata + cur_yrange * scale_factor])
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
