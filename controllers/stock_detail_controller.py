from config import STOCK_DETAIL_FRAME
from models.stock_detail_model import StockDetailModel
from views.stock_detail_window import StockDetailWindow

from .__base__ import BaseController

from datetime import datetime, timedelta
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc

class StockDetailController(BaseController):
    def __init__(self, view : StockDetailWindow, model : StockDetailModel, stock_code : str) -> None:
        self.view = view
        self.model = model
        self.frame = self.view.frames[STOCK_DETAIL_FRAME]
        self.stock_code = stock_code
        # 存放股票历史数据
        self.quotes = []

        # 连接鼠标悬浮事件和滚轮放大事件处理函数
        self.frame.canvas.mpl_connect("motion_notify_event", self.hover)
        self.frame.canvas.mpl_connect('scroll_event', self.zoom_and_pan)
        # 连接按钮的刷新数据事件
        self.frame.refresh_button.configure(command = self.refresh_data)
        # 窗口开启后默认绘制一次
        self.refresh_data()
        
    # 更新注释文本的内容和位置
    def update_annot(self, ohlc, x, y):
        date = mdates.num2date(ohlc[0]).strftime('%Y-%m-%d')
        text = f"date: {date}\nopen: {ohlc[1]}\nclose: {ohlc[2]}\nhigh: {ohlc[3]}\nlow: {ohlc[4]}"
        self.frame.annot.xy = (x, y)
        self.frame.annot.set_text(text)
        self.frame.annot.get_bbox_patch().set_alpha(0.4)

    # 鼠标悬停事件处理函数
    def hover(self, event):
        vis = self.frame.annot.get_visible()
        if event.inaxes == self.frame.ax:
            for _, bar in enumerate(self.quotes):
                if bar[0] - 0.3 <= event.xdata <= bar[0] + 0.3:
                    self.update_annot(bar, event.xdata, event.ydata)
                    self.frame.annot.set_visible(True)
                    self.frame.fig.canvas.draw_idle()
                    return
        if vis:
            self.frame.annot.set_visible(False)
            self.frame.fig.canvas.draw_idle()

    # 缩放与平移事件处理函数
    def zoom_and_pan(self, event):
        base_scale = 1.1
        if event.button == 'up' or event.button == 'down':
            if event.key == 'control':
                # 按下 Ctrl 键则代表放大或缩小
                cur_xlim = self.frame.ax.get_xlim()
                cur_xrange = max(1.0, (cur_xlim[1] - cur_xlim[0]) * 0.3)
                xdata = event.xdata
                if event.button == 'up':
                    scale_factor = 1 / base_scale
                elif event.button == 'down':
                    scale_factor = base_scale
                # 计算移动步长
                step = cur_xrange * scale_factor
                # 保证移动后不超过股价日期的上下界限
                new_low = max(xdata - step, self.model.quotes[0][0])
                new_high = min(xdata + step, self.model.quotes[-1][0])
                # 如果缩放到达边界，即某一侧到极限不能再放大或缩小，则另一侧需要弥补放大或缩小的损失。
                if new_low == self.model.quotes[0][0]:
                    if event.button == 'up':
                        new_high = cur_xlim[1] - step
                    elif event.button == 'down':
                        new_high = cur_xlim[1] + step
                    # 同样确保其不超过 quotes 范围
                    new_high = min(new_high, self.model.quotes[-1][0])
                if new_high == self.model.quotes[-1][0]:
                    if event.button == 'up':
                        new_low = cur_xlim[0] + step
                    elif event.button == 'down':
                        new_low = cur_xlim[0] - step
                    # 同样确保其不超过 quotes 范围
                    new_low = max(new_low, self.model.quotes[0][0])
                # 这是新的x轴范围
                new_xlim = [new_low, new_high]
                self.frame.ax.set_xlim(new_xlim)

                # 根据新的x轴范围计算y轴的最大最小值
                low_min, high_max = self.model.find_price_range(new_xlim[0], new_xlim[1])
                self.frame.ax.set_ylim([low_min, high_max])
            else: 
                # 平移操作
                cur_xlim = self.frame.ax.get_xlim()
                # 平移到达左右两边后不能继续平移
                if event.button == 'up' and cur_xlim[1] == self.model.quotes[-1][0]:
                    return
                if event.button == 'down' and cur_xlim[0] == self.model.quotes[0][0]:
                    return
                cur_xrange = max(1.0, (cur_xlim[1] - cur_xlim[0]) * 0.02)
                # 计算移动步长
                if event.button == 'up':
                    scale_factor = base_scale
                elif event.button == 'down':
                    scale_factor = -base_scale
                step = cur_xrange * scale_factor
                # 保证平移后不超过股价日期的上下界限
                new_low = max(cur_xlim[0] + step, self.model.quotes[0][0])
                new_high = min(cur_xlim[1] + step, self.model.quotes[-1][0])
                # 这是新的x轴范围
                new_xlim = [new_low, new_high]
                self.frame.ax.set_xlim(new_xlim)

                # 根据新的x轴范围计算y轴的最大最小值
                low_min, high_max = self.model.find_price_range(new_xlim[0], new_xlim[1])
                self.frame.ax.set_ylim([low_min, high_max])
                
            self.frame.canvas.draw_idle()

     # 刷新数据并重新绘制图表的函数
    def refresh_data(self):
        # 获取股票价格开始和结束时间
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        end_date = datetime.now().strftime('%Y%m%d')
        self.quotes = self.model.get_stock_quotes(start_date, end_date)

        # 清除旧的图表
        self.frame.ax.clear()

        # 绘制新的 K 线图
        candlestick_ohlc(self.frame.ax, self.quotes, width=0.6, colorup='r', colordown='g', alpha=0.8)
        self.frame.ax.xaxis_date()
        self.frame.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.frame.ax.grid(True)

        # 重绘图表
        self.frame.canvas.draw_idle()
        # 重新初始化注释
        self.frame.annot = self.frame.ax.annotate("", xy=(0,0), xytext=(20,20), textcoords="offset points",
                            bbox=dict(boxstyle='round', fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        self.frame.annot.set_visible(False)